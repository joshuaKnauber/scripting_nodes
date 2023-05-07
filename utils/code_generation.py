def codify_string_value(value):
    """ Takes a string and returns the code representation of it by adding quotes around it. """
    return "'" + value + "'"


def cleanup_code(value):
    """ Formats multiline code values to be indented correctly. """
    if "\n" in value:
        lines = value.split("\n")
        # remove empty lines
        lines = [*filter(lambda line: line.strip() != "", lines)]
        lines = [*map(lambda line: line.rstrip(), lines)]
        # remove indent
        min_indent = min([len(line) - len(line.lstrip())
                          for line in lines])
        lines = [line[min_indent:] for line in lines]
        value = "\n".join(lines)
    return value
