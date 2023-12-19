from googletrans import Translator


translator = Translator()


def translate_text(text: str, language: str = 'en') -> str:
    return translator.translate(
        text,
        language
    ).text
