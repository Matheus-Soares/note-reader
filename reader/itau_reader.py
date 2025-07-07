import csv
import re


class ItauReader:
    _TICKERS_FILE = 'tickers.csv'
    _NEGOCIACOES_PATTERN = r'(BOVESPA|B3 RV LISTADV|B3 RV LISTADC|B3 RV LISTA C|B3 RV LISTA V)\n(VISTA|FRACIONARIO)\n(.*)\n(?:.*?\n?)([0-9.]+)\n([0-9.]+,[0-9]{2})\n([0-9.]+,[0-9]{2})\n([CD])\n'
    _TICKER_PATTERN = r'([A-Z][A-Z][A-Z][A-Z][0-9]+)'
    _TAXA_LIQUIDACAO_PATTERN = r'(Taxa de liquidação)\n-?([0-9.]+,[0-9]{2})'
    _EMOLUMENTOS_PATTERN = r'(Emolumentos)\n-?([0-9.]+,[0-9]{2})'
    _IRRF_PATTERN = r'(I.R.R.F s/operações. Base).*\n([0-9.]+,[0-9]{2})'
    _VENDAS_PATTERN = r'(Vendas à Vista)\n([0-9.]+,[0-9]{2})'
    _COMPRAS_PATTERN = r'(Compras à Vista)\n([0-9.]+,[0-9]{2})'
    _TOTAL_OPERACOES_PATTERN = r'(Valor das operações)\n([0-9.]+,[0-9]{2})'


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

    @staticmethod
    def get_ticker_by_first_word(ticker_dict, value):
        ticker = ticker_dict.get(value)
        if ticker is not None:
            return ticker

        first_word_value = value.split()[0]
        if first_word_value == 'FII':
            return None

        for (key, value) in ticker_dict.items():
            first_word = key.split()[0]
            if first_word == first_word_value:
                return value
        return None

    def parse_ticker(self, value: str) -> str:
        matches = re.findall(self._TICKER_PATTERN, value)
        if len(matches) != 0:
            return matches[0]

        clean_value = value.replace(" EJ", "").replace(" EDJ", "")
        ticker_dict = self.get_ticker_dict()
        ticker = self.get_ticker_by_first_word(ticker_dict, clean_value)
        if ticker is not None:
            return ticker
        else:
            return self.ask_user_for_ticker(clean_value)

    @staticmethod
    def clean_string(value: str) -> str:
        return value.strip().replace('\n', '')

    def parse(self):
        self.result = {
            'negocios': [],
            'liquidacao': re.findall(self._TAXA_LIQUIDACAO_PATTERN, self._raw_text)[0][1],
            'emolumentos': re.findall(self._EMOLUMENTOS_PATTERN, self._raw_text)[0][1],
            'irrf': re.findall(self._IRRF_PATTERN, self._raw_text)[0][1],
            'vendas': self.parse_price(re.findall(self._VENDAS_PATTERN, self._raw_text)[0][1]),
            'compras': self.parse_price(re.findall(self._COMPRAS_PATTERN, self._raw_text)[0][1]),
            'total_operacoes': self.parse_price(re.findall(self._TOTAL_OPERACOES_PATTERN, self._raw_text)[0][1])
        }
        #print(self._raw_text)
        total = 0.0

        for neg in re.findall(self._NEGOCIACOES_PATTERN, self._raw_text):
            #print(neg)
            quantity = self.parse_quantity(neg[3], cv=neg[6])
            price = self.parse_price(neg[4])
            self.result['negocios'].append(
                {
                    'ticker': self.parse_ticker(neg[2]),
                    'quantity': quantity,
                    'price': price,
                }
            )
            total += round(abs(quantity) * price, 2)

        self.result['total'] = round(total, 2)
        return self.result

    def print_result(self):
        print("\nTicker\tQtd\tPreço")

        for neg in self.result['negocios']:
            print(neg['ticker'] + "\t" + str(neg['quantity']) + "\t" + str(neg['price']).replace('.', ","))

        print("\n\nTaxa de liquidação = R$ " + str(self.result['liquidacao']))
        print("Emolumentos = R$ " + str(self.result['emolumentos']))
        print("IRRF = R$ " + str(self.result['irrf']))
        print("\n\nTotal compras = R$ " + str(self.result['compras']))
        print("Total vendas = R$ " + str(self.result['vendas']))

        print("\nTotal operações lidas = R$ " + str(self.result['total']))
        print("Total operações nota = R$ " + str(self.result['total_operacoes']))

        if self.result['total'] != self.result['total_operacoes']:
            print("\n\n\033[1;31m--- Lista de negociações incompleta, necessário revisar itens lidos! ---\033[0m\n")
        else:
            print("\n\n\033[1;32m--- Lista de negociações lida com sucesso! ---\033[0m\n")

        if len(self._new_tickers) != 0:
            self.update_tickers_file()
            print("\033[1;34m--- Arquivo de tickers atualizado com " + str(
                len(self._new_tickers)) + " novos ativos! ---\033[0m\n")
