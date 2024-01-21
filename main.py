import re
import sys

import fitz

from reader.clear_reader import ClearReader
from reader.itau_reader import ItauReader
from reader.nuinvest_reader import NuInvestReader

NUINVEST_NAME = "NuInvest Corretora de Valores S.A"
CLEAR_NAME = "CLEAR CORRETORA"
ITAU_NAME = "ItaúCorretora de Valores S/A"

def extract_text(path):
    doc = fitz.open(path)
    raw_text = ""
    for page in doc:
        pdf_text = page.get_text("text")
        raw_text += re.sub('[ \u00A0]+', ' ', pdf_text)
    return raw_text


if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise Exception("Você deve informar o arquivo a ser lido. Tente Novamente")

    filepath = sys.argv[1]

    raw_text = extract_text(filepath)

    if NUINVEST_NAME in raw_text:
        reader = NuInvestReader(raw_text)
        reader.parse()
        reader.print_result()
    elif CLEAR_NAME in raw_text:
        reader = ClearReader(raw_text)
        reader.parse()
        reader.print_result()
    elif ITAU_NAME in raw_text:
        reader = ItauReader(raw_text)
        reader.parse()
        reader.print_result()
