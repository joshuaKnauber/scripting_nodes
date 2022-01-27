import bpy


class PropertySocket():
    
    def _get_python_value_parts(self):
        """ Returns the value of this property socket as parts """
        value = self.python_value
        if "," in value and "(" in value and ")" in value:
            split = value.replace("(", "").replace(")", "").split(",")
            for i in range(len(split)):
                split[i] = split[i].strip()
            return split
        return [None, "NONE"]
    
    
    @property
    def python_value_pointer(self):
        """ Returns the value of this property socket not as a tuple but as its full representation """
        parts = self._get_python_value_parts()
        value = parts[0]
        if len(parts[1]) > 2: # if prop name is not empty string
            value += f".{parts[1][1:-1]}"
        if len(parts) == 3:
            value += f"[{parts[2]}]"
        return value
    
    @property
    def python_value_source(self):
        """ Returns the value of this property socket not as a tuple but only the property source """
        parts = self._get_python_value_parts()
        value = parts[0]
        return value
    
    @property
    def python_value_name(self):
        """ Returns the value of this property socket not as a tuple but only the property name """
        parts = self._get_python_value_parts()
        return parts[1][1:-1]