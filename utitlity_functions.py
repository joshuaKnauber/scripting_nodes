def to_lower_camelcase(text):
    text = ''.join([i for i in text if not i.isdigit()])
    text = text.split(" ")
    for i, word in enumerate(text):
        text[i] = word[0].upper() + word[1:] 
    text = ("").join(text)
    text = text[0].lower() + text[1:] 
    return text   