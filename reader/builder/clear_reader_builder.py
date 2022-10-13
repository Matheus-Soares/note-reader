import re
from datetime import datetime

from reader.builder.builder_reader_base import BuilderReaderBase


class ClearReaderBuilder(BuilderReaderBase):
    NEGOCIACOES_PATTERN = '(1-BOVESPA\n)([CV]\s)(VISTA\s|FRACIONARIO\s)([A-Z0-9.\- ]+)(\n\#\n|\n)([0-9]+\n)([0-9.]+,[0-9]{2}\n)([0-9.]+,[0-9]{2}\n)([CD]\n)'

    def build_negociacoes(self):
        self.parsed_data['negocios'] = []
        for negociacao in re.findall(self.NEGOCIACOES_PATTERN, self.raw_text):
            self.parsed_data['negocios'].append(
                {
                    'titulo': self.clean_string(negociacao[3]),
                    'ticker': self.parse_ticker(self.clean_string(negociacao[3])),
                    'qtd': self.parse_qtd(negociacao[5], cv=negociacao[1]),
                    'preco': self.parse_preco(negociacao[6]),
                }
            )
