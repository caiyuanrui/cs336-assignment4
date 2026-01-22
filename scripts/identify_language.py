from fastwarc.warc import ArchiveIterator, WarcRecordType

from cs336_data.assets import assets
from cs336_data.extract import extract_text_from_html_bytes
from cs336_data.identify import identify_language


# 0.99 might be a suitable confidence threshold.
def main():
    max_len = 256
    n_samples = 32

    template = "# Record {i}\n\n## Content\n\n{content}\n\n## Identify Result\n\nLang={lang}&Score={score}"

    with open(assets.get_warc_path(), "rb") as f:
        for i, record in enumerate(ArchiveIterator(f, record_types=WarcRecordType.response)):
            html_bytes = record.reader.read()
            content = extract_text_from_html_bytes(html_bytes)
            if content is None:
                continue

            content = content[:max_len]
            lang, score = identify_language(content)

            print(template.format(i=i + 1, content=content, lang=lang, score=score))
            print("\n\n")

            if i >= n_samples - 1:
                break


if __name__ == "__main__":
    main()
