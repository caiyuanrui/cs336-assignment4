from fastwarc.warc import ArchiveIterator, WarcRecordType

from cs336_data.assets import assets
from cs336_data.extract import extract_text_from_html_bytes
from cs336_data.maskpii import mask_emails, mask_ipv4s, mask_phone_numbers


def main():
    max_records = 32
    template = """\
# Record {i}

## Raw Content

{raw}

## Masked Content w/o {type}

{masked}

"""

    with open(assets.get_warc_path(), "rb") as f:
        for i, record in enumerate(ArchiveIterator(f, record_types=WarcRecordType.response)):
            html_bytes = record.reader.read()
            content = extract_text_from_html_bytes(html_bytes)
            if content is None:
                continue

            content_without_emails, n_emails = mask_emails(content)
            content_without_ips, n_ips = mask_ipv4s(content)
            content_without_phones, n_phones = mask_phone_numbers(content)

            if n_emails > 0:
                print(template.format(i=i + 1, raw=content, masked=content_without_emails, type="email"))
            if n_ips > 0:
                print(template.format(i=i + 1, raw=content, masked=content_without_ips, type="IP"))
            if n_phones > 0:
                print(template.format(i=i + 1, raw=content, masked=content_without_phones, type="phone numbers"))

            if i + 1 >= max_records:
                break


if __name__ == "__main__":
    main()
