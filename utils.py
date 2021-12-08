import re



def get_python_name(name, replacement="", separator="_"):
    """ Returns the given name as a valid python represention to use as variable names in scripts """
    # format string
    name = name.replace(" ", separator).lower()

    # remove non alpha characters at the start
    regex = re.compile('[^a-zA-Z_]')
    name = regex.sub('', name)
    
    # return string
    if not name:
        return replacement
    return name