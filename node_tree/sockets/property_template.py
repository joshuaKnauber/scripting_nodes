import bpy


class PropertySocket():
    
    @property
    def python_value_source(self):
        """ Returns the value of this property socket not as a tuple but only the property source """
        if not self.python_value: return "None"

        parts = self.python_value.split(".")
        if len(parts) > 1:
            return ".".join(parts[:-1])
        return self.python_value
    
    @property
    def python_value_name(self):
        """ Returns the value of this property socket not as a tuple but only the property name """
        if not self.python_value: return "'None'"

        parts = self.python_value.split(".")
        if len(parts) > 1:
            return parts[-1]
        return "'None'"