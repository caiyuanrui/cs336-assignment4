from resiliparse.extract.html2text import extract_plain_text  # pyright: ignore[reportUnknownVariableType]
from resiliparse.parse.encoding import detect_encoding  # pyright: ignore[reportUnknownVariableType]


def extract_text_from_html_bytes(html_bytes: bytes) -> str | None:
    """
    Extracts html content from the given DOM node and its children,
    and returns `None` if the decoding format is undetectable or fails to parse the `html_bytes`.
    """
    enc: str | None = detect_encoding(html_bytes, html5_compatible=False)  # pyright: ignore[reportUnknownVariableType]
    if enc is None:
        return None
    try:
        html_str = html_bytes.decode(enc)  # pyright: ignore[reportUnknownArgumentType]
    except UnicodeDecodeError:
        return None
    html_content: str = extract_plain_text(html_str)  # pyright: ignore[reportUnknownVariableType]
    return html_content  # pyright: ignore[reportUnknownVariableType]
