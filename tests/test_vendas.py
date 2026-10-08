import tempfile
import unittest
from pathlib import Path

from database.connection import get_connection, initialize_database
from repositories.produto_repository import ProdutoRepository
from services.venda_service import VendaService


class VendaServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "test.db"
        initialize_database(self.database_path)
        self.produtos = ProdutoRepository(self.database_path)
        self.produto_id = self.produtos.criar("Cafe", 12.50, 8, 2)
        self.vendas = VendaService(self.database_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_finaliza_venda_calcula_troco_e_baixa_estoque(self):
        resultado = self.vendas.finalizar_venda(
            [{"produto_id": self.produto_id, "quantidade": 2}],
            forma_pagamento="Dinheiro",
            desconto=1.00,
            valor_recebido=30.00,
        )
        self.assertEqual(str(resultado["subtotal"]), "25.00")
        self.assertEqual(str(resultado["total"]), "24.00")
        self.assertEqual(str(resultado["troco"]), "6.00")
        self.assertEqual(self.produtos.buscar_por_id(self.produto_id)["estoque"], 6)
        connection = get_connection(self.database_path)
        try:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM vendas").fetchone()[0], 1)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM itens_venda").fetchone()[0], 1)
        finally:
            connection.close()

    def test_pagamento_invalido_nao_cria_venda_nem_altera_estoque(self):
        with self.assertRaisesRegex(ValueError, "menor que o total"):
            self.vendas.finalizar_venda(
                [{"produto_id": self.produto_id, "quantidade": 2}],
                forma_pagamento="Dinheiro",
                valor_recebido=10.00,
            )
        self.assertEqual(self.produtos.buscar_por_id(self.produto_id)["estoque"], 8)
        connection = get_connection(self.database_path)
        try:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM vendas").fetchone()[0], 0)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM itens_venda").fetchone()[0], 0)
        finally:
            connection.close()

    def test_agrega_produto_repetido_e_impede_estoque_insuficiente(self):
        with self.assertRaisesRegex(ValueError, "Estoque insuficiente"):
            self.vendas.finalizar_venda(
                [
                    {"produto_id": self.produto_id, "quantidade": 5},
                    {"produto_id": self.produto_id, "quantidade": 4},
                ],
                forma_pagamento="Pix",
            )
        self.assertEqual(self.produtos.buscar_por_id(self.produto_id)["estoque"], 8)


if __name__ == "__main__":
    unittest.main()
