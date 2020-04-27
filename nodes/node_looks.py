def to_percentage(hex,alpha):
    rgb = tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))
    if alpha:
        return (round(rgb[0]/255,2),round(rgb[1]/255,2),round(rgb[2]/255,2),1)
    else:
        return (round(rgb[0]/255,2),round(rgb[1]/255,2),round(rgb[2]/255,2))


socket_colors = {
    "STRING": to_percentage("cd9077",True)
}


node_colors = {
    "INTERFACE": to_percentage("367d51",False)
}


node_icons = {
    "INTERFACE": "MENU_PANEL"
}