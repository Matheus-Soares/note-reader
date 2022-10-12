import re

import fitz

from reader.models import NotaDeCorretagem


class NotaDeCorretagemReader:
    def __init__(self, filepath: str, parser=None):
        self.filepath = filepath
        self.parser = parser
        self.raw_text = ''

    def extract_text(self):
        doc = fitz.open(self.filepath)

        for page in doc:
            pdf_text = page.get_text("text")
            self.raw_text += re.sub('[ \u00A0]+', ' ', pdf_text)

    def read(self, parser=None) -> NotaDeCorretagem:
        self.extract_text()
        if not parser:
            raise Exception("You need to specify a builder in the main function.")
        return NotaDeCorretagem(**parser(self.raw_text).build())
