from reader.nota_de_corretagem_reader import NotaDeCorretagemReader

filepath = "./example.pdf"

from reader.builder.clear_reader_builder import ClearReaderBuilder
result = NotaDeCorretagemReader(filepath).read(parser=ClearReaderBuilder)

for neg in result.negocios:
    print(neg)
