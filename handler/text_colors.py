class TextColorHandler:

    def __init__(self):
        self.colors = {
            "serpens": (0,1,0.76),
            "subtext": (0.75,0.75,0.75),
            "important": (1,0.6,0.1),

            "function": (0.95,0.55,0),
            "number": (0.2,0.4,0.75),
            "string": (0,0.75,0,1),
            "data": (0.7,0.7,0.7),
            "boolean": (1,0.4,0.4),

            "red": (1,0.4,0.4),
            "blue": (0,0.3,1),
            "green": (0.05,1,0),
            "orange": (1,0.225,0),
            "yellow": (0.1,0.4,0),
            "grey": (0.6,0.6,0.6),
            "lightgrey": (0.95,0.95,0.95),
            "black": (0,0,0),
        }

    def color_by_name(self,name):
        if name in self.colors:
            return self.colors[name]
        else:
            color = name.replace("(","").replace(")","").replace(" ","").split(",")
            if len(color) == 3:
                if color[0].replace(".","").isdigit() and color[1].replace(".","").isdigit() and color[2].replace(".","").isdigit():
                    color = (float(color[0]),float(color[1]),float(color[2]))
                    return color
        return (1,1,1,1)