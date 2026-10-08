from decimal import Decimal
from pathlib import Path
from typing import Any

from config.settings import DATABASE_PATH
from database.connection import get_connection
from repositories.produto_repository import ProdutoRepository
from repositories.venda_repository import VendaRepository
from services.estoque_service import EstoqueService
from services.pagamento_service import PagamentoService
from utils.helpers import money


class VendaService:
    def __init__(
        self,
        database_path: str | Path = DATABASE_PATH,
        produto_repository: ProdutoRepository | None = None,
        venda_repository: VendaRepository | None = None,
        pagamento_service: PagamentoService | None = None,
    ):
        self.database_path = database_path
        self.produtos = produto_repository or ProdutoRepository(database_path)
        self.vendas = venda_repository or VendaRepository(database_path)
        self.pagamentos = pagamento_service or PagamentoService()

    def finalizar_venda(
        self,
        itens: list[dict[str, int]],
        forma_pagamento: str,
        desconto: Decimal | float = 0,
        valor_recebido: Decimal | float | None = None,
        usuario_id: int | None = None,
        cliente_id: int | None = None,
    ) -> dict[str, Any]:
        quantidades: dict[int, int] = {}
        for item in itens:
            produto_id = int(item["produto_id"])
            quantidade = int(item["quantidade"])
            if quantidade <= 0:
                raise ValueError("A quantidade de cada item deve ser maior que zero.")
            quantidades[produto_id] = quantidades.get(produto_id, 0) + quantidade
        if not quantidades:
            raise ValueError("Adicione pelo menos um produto a venda.")

        desconto = money(desconto)
        connection = get_connection(self.database_path)
        try:
            connection.execute("BEGIN IMMEDIATE")
            produtos = {}
            for produto_id, quantidade in quantidades.items():
                produto = self.produtos.buscar_por_id(produto_id, connection)
                if produto is None or not produto["ativo"]:
                    raise ValueError(f"Produto {produto_id} nao encontrado ou inativo.")
                if produto["estoque"] < quantidade:
                    raise ValueError(f"Estoque insuficiente para {produto['nome']}.")
                produtos[produto_id] = produto

            itens_calculados = []
            subtotal = Decimal("0.00")
            for produto_id, quantidade in quantidades.items():
                produto = produtos[produto_id]
                preco = money(produto["preco"])
                item_subtotal = money(preco * quantidade)
                subtotal += item_subtotal
                itens_calculados.append({
                    "produto_id": produto_id,
                    "quantidade": quantidade,
                    "preco_unitario": float(preco),
                    "subtotal": float(item_subtotal),
                })
            subtotal = money(subtotal)
            if desconto < 0 or desconto > subtotal:
                raise ValueError("O desconto deve estar entre zero e o subtotal.")
            total = money(subtotal - desconto)
            troco = self.pagamentos.processar(forma_pagamento, total, valor_recebido)

            venda_id = self.vendas.criar(
                connection,
                {
                    "usuario_id": usuario_id,
                    "cliente_id": cliente_id,
                    "subtotal": float(subtotal),
                    "desconto": float(desconto),
                    "total": float(total),
                    "forma_pagamento": forma_pagamento,
                },
                itens_calculados,
            )
            estoque = EstoqueService.baixar
            for produto_id, quantidade in quantidades.items():
                estoque(connection, produto_id, quantidade)
            connection.commit()
            return {
                "venda_id": venda_id,
                "subtotal": subtotal,
                "desconto": desconto,
                "total": total,
                "troco": troco,
                "forma_pagamento": forma_pagamento,
            }
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()
