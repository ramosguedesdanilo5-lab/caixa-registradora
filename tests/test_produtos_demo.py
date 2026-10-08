import tempfile
import unittest
from pathlib import Path

from database.connection import initialize_database
from repositories.produto_repository import ProdutoRepository


class ProdutosDemoTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "test.db"
        initialize_database(self.database_path)
        self.produtos = ProdutoRepository(self.database_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_catalogo_demo_e_inserido_sem_duplicatas(self):
        self.assertEqual(self.produtos.criar_produtos_demo(), 24)
        self.assertEqual(self.produtos.criar_produtos_demo(), 0)
        produtos = self.produtos.listar()
        self.assertEqual(len(produtos), 24)
        self.assertTrue(all(produto["codigo_barras"].startswith("DEMO-") for produto in produtos))
        self.assertFalse(any("coca-cola" in produto["nome"].casefold() for produto in produtos))

    def test_catalogo_demo_e_adicionado_sem_apagar_produtos_existentes(self):
        self.produtos.criar("Cafe Sao Braz 250g", 13.0, 8, 2)

        self.assertEqual(self.produtos.criar_produtos_demo(), 24)
        self.assertEqual(self.produtos.criar_produtos_demo(), 0)

        produtos = self.produtos.listar(ativos=None)
        self.assertEqual(len(produtos), 25)
        cafe = next(p for p in produtos if p["nome"] == "Cafe Sao Braz 250g")
        self.assertEqual(cafe["preco"], 13.0)
        self.assertEqual(cafe["estoque"], 8)

    def test_atualiza_descricao_demo_sem_alterar_preco_ou_estoque(self):
        self.produtos.criar("Agua mineral - 1.5 L", 3.49, 7, 2, "DEMO-100008")
        self.assertEqual(self.produtos.criar_produtos_demo(), 23)
        agua = next(p for p in self.produtos.listar() if p["codigo_barras"] == "DEMO-100008")
        self.assertEqual(agua["nome"], "Agua mineral - 500 ml")
        self.assertEqual(agua["preco"], 3.49)
        self.assertEqual(agua["estoque"], 7)


if __name__ == "__main__":
    unittest.main()