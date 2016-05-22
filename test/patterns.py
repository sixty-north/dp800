import re


def compile_pattern(pattern):
    """Compile a regex to special patterns which may contain truncated words.

    Words which may be prefix abbreviated are to be delimited with % characters
    in the pattern.

    Example:

    compile(r'%FOObar%') will produce a pattern which matches FOO, FOOB, FOOBA and FOOBAR
    """
    while True:
        match = ABBREVIATION.search(pattern)
        if not match:
            return re.compile(pattern)
        prefix, suffix = match.groups()
        pattern = pattern.replace(match.group(0), abbreviation_pattern(prefix, suffix), 1)


ABBREVIATION = re.compile(r'%([A-Z]*)([a-z]*)%')


def abbreviation_pattern(prefix, suffix, capturing=False):
    """Create a pattern for matching the abbreviated word.

    The word may contain a single hash which separates the minimum permitted abbreviation
    on the left from optional letters on the right. If no word is present, the only the
    first letter is mandatory.
    """

    open_group = '(' if capturing else '(?:'
    close_group = ')?'

    parts = [prefix] + [c.upper() for c in suffix]
    pattern = open_group.join(parts) + close_group * len(suffix)
    return pattern

