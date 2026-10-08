import tempfile
import unittest
from pathlib import Path

from database.connection import initialize_database
from repositories.produto_repository import ProdutoRepository
from services.estoque_service import EstoqueService


class EstoqueServiceTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "test.db"
        initialize_database(self.database_path)
        self.produtos = ProdutoRepository(self.database_path)
        self.produto_id = self.produtos.criar("Arroz", 8.90, 3, 3)
        self.estoque = EstoqueService(self.database_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_identifica_estoque_no_limite_minimo(self):
        baixos = self.estoque.produtos_com_estoque_baixo()
        self.assertEqual([produto["id"] for produto in baixos], [self.produto_id])

    def test_ajuste_atualiza_estoque(self):
        self.estoque.ajustar(self.produto_id, 5)
        self.assertEqual(self.produtos.buscar_por_id(self.produto_id)["estoque"], 8)

    def test_ajuste_nao_permite_estoque_negativo(self):
        with self.assertRaisesRegex(ValueError, "negativo"):
            self.estoque.ajustar(self.produto_id, -4)
        self.assertEqual(self.produtos.buscar_por_id(self.produto_id)["estoque"], 3)


if __name__ == "__main__":
    unittest.main()
