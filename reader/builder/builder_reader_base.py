from reader.ticker_dict import ticker_dict

class BuilderReaderBase:
    def __init__(self, raw_text):
        self.raw_text = raw_text
        self.parsed_data = {}

    def parse_qtd(self, value: str, cv='C'):
        value = abs(int(self.clean_string(value)))
        return value if cv.strip() == 'C' else value * -1

    def parse_preco(self, value: str) -> float:
        value = abs(float(self.clean_string(value).replace('.', '').replace(',', '.')))
        return value

    def parse_ticker(self, value: str) -> str:
        ticker = ticker_dict.get(value)
        return ticker if (ticker != None) else ''

    @staticmethod
    def clean_string(value: str) -> str:
        return value.strip().replace('\n', '')

    def build(self) -> dict:
        self.build_negociacoes()
        return self.parsed_data

    def build_negociacoes(self):
        pass
