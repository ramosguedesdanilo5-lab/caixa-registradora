from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class ItemVenda:
    produto_id: int
    nome_produto: str
    quantidade: int
    preco_unitario: Decimal

    @property
    def subtotal(self) -> Decimal:
        return self.preco_unitario * self.quantidade
