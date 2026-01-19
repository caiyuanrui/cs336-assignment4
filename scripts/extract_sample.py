from pathlib import Path
from fastwarc.warc import ArchiveIterator
from cs336_data.extract import extract_text_from_html_bytes

root_dir = Path(__file__).parent.parent
warc_path = root_dir.joinpath("data/CC-MAIN-20250417135010-20250417165010-00065.warc.gz")
wet_path = root_dir.joinpath("data/CC-MAIN-20250417135010-20250417165010-00065.warc.wet.gz")

with open(warc_path, "rb") as f:
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
