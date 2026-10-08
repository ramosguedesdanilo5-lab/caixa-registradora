from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from models.item_venda import ItemVenda


@dataclass(frozen=True)
class Venda:
    id: int
    data_hora: datetime
    subtotal: Decimal
    desconto: Decimal
    total: Decimal
    forma_pagamento: str
    itens: tuple[ItemVenda, ...] = ()
