from decimal import Decimal

from config.settings import PAYMENT_METHODS
from utils.helpers import money


class PagamentoService:
    def processar(self, forma_pagamento: str, total: Decimal | float, valor_recebido: Decimal | float | None = None) -> Decimal:
        total = money(total)
        if forma_pagamento not in PAYMENT_METHODS:
            raise ValueError("Forma de pagamento nao suportada.")
        if forma_pagamento == "Dinheiro":
            if valor_recebido is None:
                raise ValueError("Informe o valor recebido em dinheiro.")
            recebido = money(valor_recebido)
            if recebido < total:
                raise ValueError("O valor recebido e menor que o total da venda.")
            return money(recebido - total)
        return Decimal("0.00")
