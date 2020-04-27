def to_percentage(hex,alpha):
    rgb = tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))
    if alpha:
        return (round(rgb[0]/255,2),round(rgb[1]/255,2),round(rgb[2]/255,2),1)
    else:
        return (round(rgb[0]/255,2),round(rgb[1]/255,2),round(rgb[2]/255,2))


socket_colors = {
    "STRING": to_percentage("cd9077",True),
    "NUMBER": to_percentage("0048ff",True),
    "LAYOUT": to_percentage("cc3399",True),
    "BOOLEAN": to_percentage("ff9933",True),
    "VECTOR": to_percentage("ffff66",True)
}


node_colors = {
    "INTERFACE": to_percentage("367d51",False),
    "LOGIC": to_percentage("00fff5",False)
}


node_icons = {
    "INTERFACE": "MENU_PANEL",
    "LOGIC": "DRIVER_TRANSFORM"
}