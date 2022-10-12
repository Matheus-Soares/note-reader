from datetime import datetime
from typing import List

from pydantic import BaseModel


class Negocio(BaseModel):
    titulo: str
    ticker: str
    qtd: int
    preco: float

    def __str__(self):
        return "" + self.titulo + "," + self.ticker + "," + str(self.qtd) + "," + str(self.preco)

class NotaDeCorretagem(BaseModel):
    negocios: List[Negocio]