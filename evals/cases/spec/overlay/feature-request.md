# Slugify label feature request

Add a dependency-free `slugify_label(value: str)` beside `normalize_label` in `src/reporter/text_tools.py`. It trims surrounding whitespace, lowercases ASCII letters, and replaces each run of internal whitespace with one hyphen.

Whitespace is any character Python's `str.isspace()` accepts, so non-ASCII whitespace such as U+00A0 and U+3000 is trimmed and collapsed exactly like a space. Every other non-ASCII character is preserved unchanged, case included - which is where it parts from `normalize_label`.

The FIS must cover empty-after-trim input by returning the empty string, and the contract it binds proof to is these three calls: `slugify_label('  MiXeD   Label  ')` is `'mixed-label'`, `slugify_label('   ')` is `''`, and `slugify_label(' Å  LABEL ')` is `'Å-label'`.

Do not add a command-line flag, a web API, persistence, telemetry, or a third-party package.
