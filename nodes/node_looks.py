def to_percentage(hex,alpha):
    rgb = tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))
    if alpha:
        return (round(rgb[0]/255,2),round(rgb[1]/255,2),round(rgb[2]/255,2),1)
    else:
        return (round(rgb[0]/255,2),round(rgb[1]/255,2),round(rgb[2]/255,2))


socket_colors = {
    "STRING": to_percentage("63C763",True),
    "NUMBER": to_percentage("A1A1A1",True),
    "LAYOUT": to_percentage("ed5700",True),
    "BOOLEAN": to_percentage("2A5CFF",True),
    "VECTOR": to_percentage("6363C7",True)
}


node_colors = {
    "INTERFACE": to_percentage("A5CFC9",False),
    "LOGIC": to_percentage("4D4D4D",False),
    "INPUT": to_percentage("ACACAC",False)
}


node_icons = {
    "INTERFACE": "MENU_PANEL",
    "LOGIC": "DRIVER_TRANSFORM",
    "INPUT": "NODE"
}