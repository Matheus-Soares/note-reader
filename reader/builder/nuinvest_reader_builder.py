import re
from datetime import datetime

from reader.builder.builder_reader_base import BuilderReaderBase


class NuinvestReaderBuilder(BuilderReaderBase):
    NEGOCIACOES_PATTERN = '(BOVESPA\n)([CV]\n)(VISTA\n|FRACIONARIO\n)([A-Z][A-Z][A-Z][A-Z][0-9]+[A-Z]*)(\s\w*[\#\n|\n])([0-9]+\n)([0-9.]+,[0-9]{2}\n)([0-9.]+,[0-9]{2}\n)([CD]\n)'

    def build_negociacoes(self):
        self.parsed_data['negocios'] = []
        for negociacao in re.findall(self.NEGOCIACOES_PATTERN, self.raw_text):
            self.parsed_data['negocios'].append(
                {
                    'titulo': '',
                    'ticker': self.clean_string(negociacao[3]),
                    'qtd': self.parse_qtd(negociacao[5], cv=negociacao[1]),
                    'preco': self.parse_preco(negociacao[6]),
                }
            )
