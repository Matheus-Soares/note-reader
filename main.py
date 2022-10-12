import sys

from reader.nota_de_corretagem_reader import NotaDeCorretagemReader
from reader.builder.clear_reader_builder import ClearReaderBuilder

if __name__ == '__main__':
    if (len(sys.argv) < 2):
        raise Exception("Você deve informar o arquivo a ser lido.")
    filepath = sys.argv[1]
    result = NotaDeCorretagemReader(filepath).read(parser=ClearReaderBuilder)

    print("Título,Ticker,Qtd,Preço")
    for neg in result.negocios:
        print(neg)
