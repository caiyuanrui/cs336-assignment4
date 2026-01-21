from fastwarc import ArchiveIterator
from fastwarc.warc import WarcRecordType
from fasttext import load_model  # pyright: ignore[reportUnknownVariableType]

from cs336_data.classify import classify_nsfw, classify_toxic_speech
from cs336_data.extract import extract_text_from_html_bytes
from cs336_data.utils import nsfw_model_path, warc_sample_path, hatespeech_model_path


def main():
    nsfw_model = load_model(nsfw_model_path())
    toxic_model = load_model(hatespeech_model_path())

    n_samples = 20
    template = """\
# Record/Line {i}/{j}

## Line

{raw}

## Labels & Scores

1. {nsfw_lb}={nsfw_score}
2. {toxic_lb}={toxic_score}

"""

    output_buffer = {"nsfw": [], "toxic": []}  # pyright: ignore[reportUnknownVariableType]

    with open(warc_sample_path(), "rb") as f:
        for record in ArchiveIterator(f, record_types=WarcRecordType.response):
            html_bytes = record.reader.read()

            content = extract_text_from_html_bytes(html_bytes)

            if content is None:
                continue

            for line in content.splitlines():
                nsfw_lb, nsfw_score = classify_nsfw(line, nsfw_model)
                toxic_lb, toxic_score = classify_toxic_speech(line, toxic_model)

                entry = {"line": line, nsfw_lb: nsfw_score, toxic_lb: toxic_score}

                if nsfw_lb == "nsfw" and len(output_buffer["nsfw"]) < n_samples:  # pyright: ignore[reportUnknownArgumentType]
                    output_buffer["nsfw"].append(entry)
                    print(entry)

                if toxic_lb == "toxic" and len(output_buffer["toxic"]) < n_samples:  # pyright: ignore[reportUnknownArgumentType]
                    output_buffer["toxic"].append(entry)
                    print(entry)


if __name__ == "__main__":
    main()
