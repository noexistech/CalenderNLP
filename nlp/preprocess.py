# nlp/preprocess.py
from underthesea import word_tokenize

def preprocess(text: str):
    # 1) tokenize
    tokens = word_tokenize(text)

    # 2) convert "kết_thúc" → "kết thúc", "thứ_hai" → "thứ hai"
    text_clean = " ".join(tokens).replace("_", " ")
    
    return text_clean.split()
