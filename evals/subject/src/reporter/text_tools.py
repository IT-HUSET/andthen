"""Label text helpers. Pure functions, no I/O, no imports from this package."""


def normalize_label(text):
    """Collapse runs of whitespace and lowercase a label."""
    if not isinstance(text, str):
        raise TypeError("label must be a string")
    return " ".join(text.split()).lower()

