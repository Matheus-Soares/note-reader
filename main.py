import re
import sys

import fitz

from reader.itau_reader import ItauReader
from reader.nuinvest_reader import NuInvestReader
from reader.sinacor_reader import SinacorReader

NUINVEST_NAME = "NuInvest Corretora de Valores S.A"
ITAU_NAME = "ItaúCorretora de Valores S/A"


def extract_text(path):
    doc = fitz.open(path)
    text = ""
    for page in doc:
        pdf_text = page.get_text("text")
        text += re.sub('[ \u00A0]+', ' ', pdf_text)
    return text


if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise Exception("Você deve informar o arquivo a ser lido. Tente Novamente")

    filepath = sys.argv[1]

    raw_text = extract_text(filepath)

    if NUINVEST_NAME in raw_text:
        print("Lendo Nota de Corretagem Padrão NuInvest")
        reader = NuInvestReader(raw_text)
        reader.parse()
        reader.print_result()
    elif ITAU_NAME in raw_text:
        print("Lendo Nota de Corretagem Padrão Itaú")
        reader = ItauReader(raw_text)
        reader.parse()
        reader.print_result()
    else:
        print("Lendo Nota de Corretagem Padrão Sinacor")
        reader = SinacorReader(raw_text)
        reader.parse()
        reader.print_result()
