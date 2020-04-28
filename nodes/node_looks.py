def to_percentage(hex,alpha):
    rgb = tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))
    if alpha:
        return (round(rgb[0]/255,2),round(rgb[1]/255,2),round(rgb[2]/255,2),1)
    else:
        return (round(rgb[0]/255,2),round(rgb[1]/255,2),round(rgb[2]/255,2))


socket_colors = {
    "STRING": to_percentage("10E55D",True),
    "NUMBER": to_percentage("A1A1A1",True),
    "LAYOUT": to_percentage("F1B01A",True),
    "BOOLEAN": to_percentage("2A5CFF",True),
    "VECTOR": to_percentage("6363C7",True),
    "PROGRAM": to_percentage("F81033",True)
}


node_colors = {
    "INTERFACE": to_percentage("A17835",False),
    "LOGIC": to_percentage("4D4D4D",False),
    "INPUT": to_percentage("ACACAC",False),
    "FUNCTION": to_percentage("A13546",False)
}


node_icons = {
    "INTERFACE": "RESTRICT_VIEW_OFF",
    "LOGIC": "CONSOLE",
    "INPUT": "DRIVER_TRANSFORM",
    "FUNCTION": "SCRIPT"
}