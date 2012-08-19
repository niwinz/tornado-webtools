
def smart_bytes(value, encoding='utf-8', errors='strict'):
    if isinstance(value, bytes):
        if encoding == 'utf-8':
            return value

        return value.decode('utf-8', errors).encode(encoding, errors)

    if not isinstance(value, str):
        value = str(value)

    return value.encode(encoding, errors)

def smart_text(value, encoding="utf-8", errors="strict"):
    if isinstance(value, str):
        if encoding == "utf-8":
            return value

        return value.encode('utf-8', errors).decode(encoding, errors)

    if not isinstance(value, bytes):
        return str(value)

    return value.decode(encoding, errors)
