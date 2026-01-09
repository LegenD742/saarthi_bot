def detect_language(text):
    hindi_chars = any('\u0900' <= c <= '\u097F' for c in text)
    return "hi" if hindi_chars else "en"