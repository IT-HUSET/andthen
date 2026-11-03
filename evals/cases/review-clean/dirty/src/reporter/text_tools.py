"""Label text helpers. Pure functions, no I/O, no imports from this package."""

ELLIPSIS = "..."


def normalize_label(text):
    """Collapse runs of whitespace and lowercase a label."""
    if not isinstance(text, str):
        raise TypeError("label must be a string")
    return " ".join(text.split()).lower()


def truncate_label(text, limit):
    """Cut `text` to at most `limit` characters, ending in an ellipsis when it was cut."""
    if not isinstance(text, str):
        raise TypeError("label must be a string")
    if limit < len(ELLIPSIS):
        raise ValueError("limit must be at least %d" % len(ELLIPSIS))
    if len(text) <= limit:
        return text
    return text[:limit - len(ELLIPSIS)] + ELLIPSIS
