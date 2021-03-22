#!D:\python38\python.exe

from fixer import Fixer
import cgi


class Arguments:

    def __init__(self, source_lang: str, target_lang: str):
        self.recalculate = False
        self.approximately = True
        self.source_lang = source_lang
        self.target_lang = target_lang


if __name__ == "__main__":
    print("Content-type: text/html\r\n")

    form = cgi.FieldStorage()
    src_lang = form.getvalue('src')
    tgt_lang = form.getvalue('tgt')

    fixer = Fixer(Arguments(src_lang, tgt_lang))

    src_text = form.getvalue('source_text')
    tgt_text = form.getvalue('target_text')

    translation = fixer.fix(src_text, tgt_text)

    # there was no fix or the sentence is unfixable
    if not translation or translation is True:
        translation = tgt_text

    print(translation)
