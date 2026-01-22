# pyright: reportUnknownVariableType = false
# pyright: reportUnknownVariableType = false
from resiliparse.extract.html2text import extract_plain_text
from resiliparse.parse.encoding import detect_encoding


def extract_text_from_html_bytes(html_bytes: bytes) -> str | None:
    """
    Extracts html content from the given DOM node and its children,
    and returns `None` if the decoding format is undetectable or fails to parse the `html_bytes`.
    """
    enc = detect_encoding(html_bytes, html5_compatible=False)
    if not isinstance(enc, str):
        return None
    try:
        html_str = html_bytes.decode(enc)
    except UnicodeDecodeError:
        return None
    html_content: str = extract_plain_text(html_str)
    return html_content
