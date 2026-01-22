from fastwarc.warc import ArchiveIterator

from cs336_data.assets import assets
from cs336_data.extract import extract_text_from_html_bytes

with open(assets.get_warc_path(), "rb") as f:
    for i, record in enumerate(ArchiveIterator(f)):
        html_bytes = record.reader.read()
        content = extract_text_from_html_bytes(html_bytes)
        print(f"============================ {i} ===========================")
        if content is None:
            print(content)
        else:
            print(content[:1024])
        if i > 5:
            break
