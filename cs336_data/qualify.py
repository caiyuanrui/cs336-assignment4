from pathlib import Path

from fastwarc.warc import ArchiveIterator, WarcRecordType
from regex import Regex

from cs336_data.assets import assets
from cs336_data.extract import extract_text_from_html_bytes
from cs336_data.fasttext_model import FastTextModel
from cs336_data.identify import identify_language


def gopher_quality_filter(text: str, model_langid: FastTextModel | None = None) -> bool:
    """
    Returns False if any conditions is satisfied:
        - Not in English.
        - Contain less than 50 or more than 100,000 words.
        - Have a mean word length outside the range of 3 to 10 characters.
        - Have more than 30% of lines ending with an ellipsis (“...”).
        - Contain less than 80% of words with at least one alphabetic character.
    """
    lang, score = identify_language(text, model_langid)
    if lang != "__label__en" or score < 0.8:
        return False

    word_total_length = 0
    word_count = 0
    line_count = 0
    sufix_ellipsis = 0
    include_alphabet = 0

    for line in text.splitlines():
        line_count += 1
        if line[-3:] == "...":
            sufix_ellipsis += 1
        for word in line.split(" "):
            if len(word) == 0:
                continue
            word_total_length += len(word)
            word_count += 1
            if any(c.isalpha() for c in word):
                include_alphabet += 1

    avg_word_length = word_total_length / word_count

    if (
        word_count < 50
        or word_count > 100000
        or avg_word_length < 3
        or avg_word_length > 10
        or sufix_ellipsis / line_count > 0.3
        or include_alphabet / word_count < 0.8
    ):
        return False

    return True


def generate_positive_data(path: Path):
    langid = FastTextModel(assets.get_language_classifier_path().as_posix())
    with open(path, "rb") as warc_f:
        for record in ArchiveIterator(warc_f, record_types=WarcRecordType.response):
            html_bytes = record.reader.read()
            text = extract_text_from_html_bytes(html_bytes)
            if text is None or not gopher_quality_filter(text, langid):
                continue
            yield text


def quality_classifier():
    return assets.get_quality_classifier()


def classify_quality(text: str, model: FastTextModel | None = None):
    if model is None:
        model = assets.get_quality_classifier()
    text = Regex("\n+").sub(" ", text)
    label, score = model.predict(text)
    if label == "__label__Low":
        label = "cc"
    else:
        label = "wiki"
    return label, score


if __name__ == "__main__":
    model = FastTextModel(assets.get_language_classifier_path().as_posix())
    text = "This should definitely be a valid sentence. You shall never filter it!" * 100
    print(gopher_quality_filter(text, model))
