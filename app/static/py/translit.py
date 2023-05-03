from transliterate import translit as trnslt, exceptions

def translit(string: str, lang_code: str = None):
    try:
        return trnslt(string, lang_code, reversed=True)
    except exceptions.LanguageDetectionError:
        return string
