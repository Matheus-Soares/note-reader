import re
import sys

import fitz

NEGOCIACOES_PATTERN = '(BOVESPA)\n([CV])\n(VISTA|FRACIONARIO)\n([A-Z][A-Z][A-Z][A-Z][0-9]+)[A-Z]*.*\n(?:#?\n?)([0-9.]+)\n([0-9.]+,[0-9]{2})\n([0-9.]+,[0-9]{2})\n([CD])\n'
TAXA_LIQUIDACAO_PATTERN = '(Taxa de Liquidação)\n-?([0-9.]+,[0-9]{2})'
EMOLUMENTOS_PATTERN = '(Emolumentos)\n-?([0-9.]+,[0-9]{2})'
IRRF_PATTERN = '(I.R.R.F. s/ operações. Base).*\n([0-9.]+,[0-9]{2})'
VENDAS_PATTERN = '(Vendas à vista)\n([0-9.]+,[0-9]{2})'
COMPRAS_PATTERN = '(Compras à vista)\n([0-9.]+,[0-9]{2})'
TOTAL_OPERACOES_PATTERN = '(Valor das Operações)\n([0-9.]+,[0-9]{2})'


def parse_qtd(value: str, cv='C'):
    value = abs(int(clean_string(value).replace('.', '')))
    return value if cv.strip() == 'C' else value * -1


def parse_preco(value: str) -> float:
    value = abs(float(clean_string(value).replace('.', '').replace(',', '.')))
    return value


def clean_string(value: str) -> str:
    return value.strip().replace('\n', '')


def extract_text(path):
    doc = fitz.open(path)
    raw_text = ""
    for page in doc:
        pdf_text = page.get_text("text")
        raw_text += re.sub('[ \u00A0]+', ' ', pdf_text)
    return raw_text


def read_nuinvest(path: str):
    raw_text = extract_text(path)
    parsed_data = {
        'negocios': [],
        'liquidacao': re.findall(TAXA_LIQUIDACAO_PATTERN, raw_text)[0][1],
        'emolumentos': re.findall(EMOLUMENTOS_PATTERN, raw_text)[0][1],
        'irrf': re.findall(IRRF_PATTERN, raw_text)[0][1],
        'vendas': parse_preco(re.findall(VENDAS_PATTERN, raw_text)[0][1]),
        'compras': parse_preco(re.findall(COMPRAS_PATTERN, raw_text)[0][1]),
        'total_operacoes': parse_preco(re.findall(TOTAL_OPERACOES_PATTERN, raw_text)[0][1])
    }
    total = 0.0

    for negociacao in re.findall(NEGOCIACOES_PATTERN, raw_text):
        qtd = parse_qtd(negociacao[4], cv=negociacao[1])
        preco = parse_preco(negociacao[5])
        parsed_data['negocios'].append(
            {
                'ticker': clean_string(negociacao[3]),
                'qtd': qtd,
                'preco': preco,
            }
        )
        qtd_preco = round(abs(qtd) * preco, 2)
        total += qtd_preco

    parsed_data['total'] = round(total, 2)
    return parsed_data


def print_values(result):
    print("Ticker,Qtd,Preço")

    for neg in result['negocios']:
        print(neg['ticker'] + ";" + str(neg['qtd']) + ";" + str(neg['preco']).replace('.', ","))

    print("\n\nTaxa de liquidação = R$ " + str(result['liquidacao']))
    print("Emolumentos = R$ " + str(result['emolumentos']))
    print("IRRF = R$ " + str(result['irrf']))
    print("\n\nTotal vendas = R$ " + str(result['vendas']))
    print("Total compras = R$ " + str(result['compras']))

    print("\nTotal operações lidas = R$ " + str(result['total']))
    print("Total operações nota = R$ " + str(result['total_operacoes']))

    if result['total'] != result['total_operacoes']:
        print("\n\n\033[1;31m--- Lista de negociações incompleta, necessário revisar itens lidos! ---\033[0m\n")
    else:
        print("\n\n\033[1;32m--- Lista de negociações lida com sucesso! ---\033[0m\n")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise Exception("Você deve informar o arquivo a ser lido. Tente Novamente")

    filepath = sys.argv[1]

    result = read_nuinvest(filepath)

    print_values(result)
