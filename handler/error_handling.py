import bpy

class ErrorHandler():

    # CALLABLE FUNCTIONS
    # handle_text: takes in text and returns the updated text to use in the file

    def handle_text(text):
        """ returns the updated text without errors """
        
        invalid_texts = ["and", "as", "assert", "async", "await", "break", "class", "continue", "def", "del", "elif", "else", "except", "False", "finally", "for", "from", "global", "if", "import", "in", "is", "lambda", "None", "nonlocal", "not", "or", "pass", "raise", "return", "True", "try", "while", "with", "yield"]

        if text.replace(" ", "") in invalid_texts:
            text = text.replace(" ", "")+="_"

        invalid_caracters = ["(", ")", "#"]

        for caracter in invalid_caracters:
            if caracter in text:
                text = text.replace(caracter, "")

        return text