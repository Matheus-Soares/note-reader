import csv
import re


class ClearReader:
    _TICKERS_FILE = 'tickers.csv'
    _NEGOCIACOES_PATTERN = '(1-BOVESPA)\n([CV])\s(VISTA|FRACIONARIO)\n(.*)\n(?:.*?\n?)([0-9.]+)\n([0-9.]+,[0-9]{2})\n([0-9.]+,[0-9]{2})\n([CD])\n'
    _TICKER_PATTERN = '([A-Z][A-Z][A-Z][A-Z][0-9]+)'
    _TAXA_LIQUIDACAO_PATTERN = '([0-9.]+,[0-9]{2})\nTaxa de liquidação'
    _EMOLUMENTOS_PATTERN = '([0-9.]+,[0-9]{2})\nEmolumentos'
    _IRRF_PATTERN = '([0-9.]+,[0-9]{2})\nI.R.R.F. s/ operações'
    _TOTAL_OPERACOES_PATTERN = '([0-9.]+,[0-9]{2})\nResumo dos Negócios'

    def __init__(self, raw_text):
        self._raw_text = raw_text
        self._result = {}
        self._ticker_dict = None
        self._new_tickers = {}

    def parse_quantity(self, value: str, cv='C') -> int:
        cleaned_str = self.clean_string(value).replace('.', '')
        value = abs(int(cleaned_str))
        return value if cv.strip() == 'C' else value * -1

    def parse_price(self, value: str) -> float:
        cleaned_str = self.clean_string(value).replace('.', '').replace(',', '.')
        value = abs(float(cleaned_str))
        return value

    def update_tickers_file(self):
        with open(self._TICKERS_FILE, 'a', newline='') as file:
            writer = csv.writer(file)
            for name, ticker in self._new_tickers.items():
                writer.writerow([name, ticker])

    def ask_user_for_ticker(self, operation) -> str:
        ticker = input("Digite o ticker da ação \033[1m" + operation + "\033[0m: ")
        self._ticker_dict[operation] = ticker
        self._new_tickers[operation] = ticker
        return ticker

    def get_ticker_dict(self) -> dict:
        if self._ticker_dict is None:
            self._ticker_dict = {}
            with open(self._TICKERS_FILE, mode='r') as file:
                reader = csv.reader(file)
                for row in reader:
                    self._ticker_dict[row[0]] = row[1]
        return self._ticker_dict

    def parse_ticker(self, value: str) -> str:
        matches = re.findall(self._TICKER_PATTERN, value)
        if len(matches) != 0:
            return matches[0]

        ticker = self.get_ticker_dict().get(value)
        if ticker is not None:
            return ticker
        else:
            return self.ask_user_for_ticker(value)

    @staticmethod
    def clean_string(value: str) -> str:
        return value.strip().replace('\n', '')

    def parse(self):
        self._result = {
            'negocios': [],
            'liquidacao': re.findall(self._TAXA_LIQUIDACAO_PATTERN, self._raw_text)[0],
            'emolumentos': re.findall(self._EMOLUMENTOS_PATTERN, self._raw_text)[0],
            'irrf': re.findall(self._IRRF_PATTERN, self._raw_text)[0],
            'total_operacoes': self.parse_price(re.findall(self._TOTAL_OPERACOES_PATTERN, self._raw_text)[0])
        }
        total = 0.0

        for neg in re.findall(self._NEGOCIACOES_PATTERN, self._raw_text):
            quantity = self.parse_quantity(neg[4], cv=neg[1])
            price = self.parse_price(neg[5])
            self._result['negocios'].append(
                {
                    'ticker': self.parse_ticker(neg[3]),
                    'quantity': quantity,
                    'price': price,
                }
            )
            total += round(abs(quantity) * price, 2)

        self._result['total'] = round(total, 2)
        return self._result

    def print_result(self):
        print("\n\nTicker,Qtd,Preço")

        for neg in self._result['negocios']:
            print(neg['ticker'] + ";" + str(neg['quantity']) + ";" + str(neg['price']).replace('.', ","))

        print("\n\nTaxa de liquidação = R$ " + str(self._result['liquidacao']))
        print("Emolumentos = R$ " + str(self._result['emolumentos']))
        print("IRRF = R$ " + str(self._result['irrf']))

        print("\nTotal operações lidas = R$ " + str(self._result['total']))
        print("Total operações nota = R$ " + str(self._result['total_operacoes']))

        if self._result['total'] != self._result['total_operacoes']:
            print("\n\n\033[1;31m--- Lista de negociações incompleta, necessário revisar itens lidos! ---\033[0m\n")
        else:
            print("\n\n\033[1;32m--- Lista de negociações lida com sucesso! ---\033[0m")

        if len(self._new_tickers) != 0:
            self.update_tickers_file()
            print("\033[1;34m--- Arquivo de tickers atualizado com " + str(
                len(self._new_tickers)) + " novos ativos! ---\033[0m\n")
