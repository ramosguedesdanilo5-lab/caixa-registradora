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

    def test_catalogo_demo_e_criado_apenas_quando_nao_ha_produtos(self):
        self.assertEqual(self.produtos.criar_catalogo_demo_se_vazio(), 24)
        self.assertEqual(self.produtos.criar_catalogo_demo_se_vazio(), 0)
        self.assertEqual(len(self.produtos.listar()), 24)

        self.produtos.criar("Produto cadastrado", 2.0, 5, 1)
        self.assertEqual(self.produtos.criar_catalogo_demo_se_vazio(), 0)
        self.assertEqual(len(self.produtos.listar(ativos=None)), 25)

    def test_atualiza_descricao_demo_sem_alterar_preco_ou_estoque(self):
        self.produtos.criar("Agua mineral - 1.5 L", 3.49, 7, 2, "DEMO-100008")
        self.assertEqual(self.produtos.criar_produtos_demo(), 23)
        agua = next(p for p in self.produtos.listar() if p["codigo_barras"] == "DEMO-100008")
        self.assertEqual(agua["nome"], "Agua mineral - 500 ml")
        self.assertEqual(agua["preco"], 3.49)
        self.assertEqual(agua["estoque"], 7)


if __name__ == "__main__":
    unittest.main()