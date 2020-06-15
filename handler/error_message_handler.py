import bpy

class ErrorMessageHandler():

    # CALLABLE FUNCTIONS
    # handle_text: takes in text and returns the updated text to use in the file

    errors = {
        "test_error": {
            "name": "Test error",
            "message": "this is the errors description",
            "fatal": True
        }
    }

    def error_name(self, key):
        """ returns the error name for the given error """
        if key in self.errors:
            return self.errors[key]["name"]
        return ""

    def error_message(self, key):
        """ returns the error message for the given error """
        if key in self.errors:
            return self.errors[key]["message"]
        return ""

    def error_fatal(self, key):
        """ returns if the error is fatal for the given error """
        if key in self.errors:
            return self.errors[key]["fatal"]
        return False