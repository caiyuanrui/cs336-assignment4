from regex import Regex


def _mask(pattern: str, old_text: str, repl: str):
    re = Regex(pattern)
    new_text: str = ""
    i = 0
    cnt = 0

    for match in re.finditer(old_text):
        s, e = match.span()
        new_text += old_text[i:s] + repl
        i = e
        cnt += 1

    new_text += old_text[i:]

    return new_text, cnt


def mask_emails(text: str):
    return _mask(r"[\w.]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,10}", text, "|||EMAIL_ADDRESS|||")


def mask_phone_numbers(text: str):
    return _mask(r"[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}", text, "|||PHONE_NUMBER|||")


def mask_ipv4s(text: str):
    return _mask(r"(?:[0-9]{1,3}\.){3}[0-9]{1,3}", text, "|||IP_ADDRESS|||")
