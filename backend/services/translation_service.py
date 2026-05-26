from deep_translator import GoogleTranslator
from langdetect import detect_langs, LangDetectException

def detect_lang(text: str) -> str:
    t = text.strip().lower()

    if not t:
        return "en"

    # Native scripts first
    if any('\u0980' <= ch <= '\u09FF' for ch in t):
        return "bn"

    if any('\u0900' <= ch <= '\u097F' for ch in t):
        return "hi"

    # Roman Bengali hints
    bn_words = [
        "kothai", "kothay", "ache", "ki", "eta",
        "korbo", "bolo", "dekhao", "kivabe"
    ]

    tokens = t.split()

    if any(word in tokens for word in bn_words):
        return "bn"

    # Roman Hindi hints
    hi_words = [
        "kaha", "hai", "kaise", "kya",
        "dikhao", "batao", "kaun"
    ]

    if any(word in tokens for word in hi_words):
        return "hi"

    # Short ambiguous text
    if len(t) < 5:
        return "en"

    try:
        best = detect_langs(t)[0]

        if best.prob < 0.55:
            return "en"

        return best.lang

    except:
        return "en"


def to_english(text: str) -> str:
    lang = detect_lang(text)

    if lang == "en":
        return text

    try:
        return GoogleTranslator(source="auto", target="en").translate(text)
    except:
        return text


def translate_back(text: str, lang: str) -> str:
    if lang == "en":
        return text

    try:
        return GoogleTranslator(source="auto", target=lang).translate(text)
    except:
        return text