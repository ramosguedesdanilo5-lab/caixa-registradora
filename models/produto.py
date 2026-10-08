from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Produto:
    id: int
    nome: str
    preco: Decimal
    estoque: int
    estoque_minimo: int
    codigo_barras: str | None = None
    ativo: bool = True
