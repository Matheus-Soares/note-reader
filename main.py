import sys

from reader.nota_de_corretagem_reader import NotaDeCorretagemReader
from reader.builder.clear_reader_builder import ClearReaderBuilder
from reader.builder.nuinvest_reader_builder import NuinvestReaderBuilder

if __name__ == '__main__':
    if (len(sys.argv) < 2):
        raise Exception("Você deve informar o arquivo a ser lido.")
    filepath = sys.argv[1]
    
    if (len(sys.argv) == 3):
        builder = sys.argv[2]
    else:
        builder = 'nuinvest'
    
    if (builder == 'clear'):
        print("clear")
        result = NotaDeCorretagemReader(filepath).read(parser=ClearReaderBuilder)
    else:
        result = NotaDeCorretagemReader(filepath).read(parser=NuinvestReaderBuilder)


    print("Título,Ticker,Qtd,Preço")
    for neg in result.negocios:
        print(neg)
