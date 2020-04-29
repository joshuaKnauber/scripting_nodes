def to_lower_camelcase(text):
    text = ''.join([i for i in text if not i.isdigit()])
    text = text.title()
    text = text.replace(" ","")
    text = text[0].lower() + text[1:] 
    return text