import re


class NuInvestReader:
    _NEGOCIACOES_PATTERN = r'(BOVESPA)\n([CV])\n(VISTA|FRACIONARIO)\n([A-Z][A-Z][A-Z][A-Z][0-9]+)[A-Z]*.*\n(?:#?D?\n?)([0-9.]+)\n([0-9.]+,[0-9]{2})\n([0-9.]+,[0-9]{2})\n([CD])\n'
    _TAXA_LIQUIDACAO_PATTERN = r'(Taxa de Liquidação)\n-?([0-9.]+,[0-9]{2})'
    _EMOLUMENTOS_PATTERN = r'(Emolumentos)\n-?([0-9.]+,[0-9]{2})'
    _IRRF_PATTERN = r'(I.R.R.F. s/ operações. Base).*\n([0-9.]+,[0-9]{2})'
    _VENDAS_PATTERN = r'(Vendas à vista)\n([0-9.]+,[0-9]{2})'
    _COMPRAS_PATTERN = r'(Compras à vista)\n([0-9.]+,[0-9]{2})'
    _TOTAL_OPERACOES_PATTERN = r'(Valor das Operações)\n([0-9.]+,[0-9]{2})'

    def __init__(self, raw_text):
        self._raw_text = raw_text
        self._result = {}

    def parse_quantity(self, value: str, cv='C') -> int:
        cleaned_str = self.clean_string(value).replace('.', '')
        value = abs(int(cleaned_str))
        return value if cv.strip() == 'C' else value * -1

    def parse_price(self, value: str) -> float:
        cleaned_str = self.clean_string(value).replace('.', '').replace(',', '.')
        value = abs(float(cleaned_str))
        return value

    @staticmethod
    def clean_string(value: str) -> str:
        return value.strip().replace('\n', '')

    def parse(self):
        self._result = {
            'negocios': [],
            'liquidacao': re.findall(self._TAXA_LIQUIDACAO_PATTERN, self._raw_text)[0][1],
            'emolumentos': re.findall(self._EMOLUMENTOS_PATTERN, self._raw_text)[0][1],
            'irrf': re.findall(self._IRRF_PATTERN, self._raw_text)[0][1],
            'vendas': self.parse_price(re.findall(self._VENDAS_PATTERN, self._raw_text)[0][1]),
            'compras': self.parse_price(re.findall(self._COMPRAS_PATTERN, self._raw_text)[0][1]),
            'total_operacoes': self.parse_price(re.findall(self._TOTAL_OPERACOES_PATTERN, self._raw_text)[0][1])
        }
        total = 0.0

        for neg in re.findall(self._NEGOCIACOES_PATTERN, self._raw_text):
            quantity = self.parse_quantity(neg[4], cv=neg[1])
            price = self.parse_price(neg[5])
            self._result['negocios'].append(
                {
                    'ticker': self.clean_string(neg[3]),
                    'quantity': quantity,
                    'price': price,
                }
            )
            total += round(abs(quantity) * price, 2)

        self._result['total'] = round(total, 2)
        return self._result

    def print_result(self):
        print("\nTicker\tQtd\tPreço")

        for neg in self._result['negocios']:
            print(neg['ticker'] + "\t" + str(neg['quantity']) + "\t" + str(neg['price']).replace('.', ","))

        print("\n\nTaxa de liquidação = R$ " + str(self._result['liquidacao']))
        print("Emolumentos = R$ " + str(self._result['emolumentos']))
        print("IRRF = R$ " + str(self._result['irrf']))
        print("\n\nTotal compras = R$ " + str(self._result['compras']))
        print("Total vendas = R$ " + str(self._result['vendas']))

        print("\nTotal operações lidas = R$ " + str(self._result['total']))
        print("Total operações nota = R$ " + str(self._result['total_operacoes']))

        if self._result['total'] != self._result['total_operacoes']:
            print("\n\n\033[1;31m--- Lista de negociações incompleta, necessário revisar itens lidos! ---\033[0m\n")
        else:
            print("\n\n\033[1;32m--- Lista de negociações lida com sucesso! ---\033[0m\n")
