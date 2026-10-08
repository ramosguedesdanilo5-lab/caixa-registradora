import unittest

from repositories.produto_repository import ProdutoRepository
from ui.caixa import _product_image


class ProdutoImageMappingTests(unittest.TestCase):
    def test_todos_os_produtos_demo_tem_imagem_e_nome_generico(self):
        for index, (nome, _, _, _, codigo_barras) in enumerate(ProdutoRepository.DEMO_PRODUCTS, start=1):
            with self.subTest(nome=nome):
                produto = {"id": index, "nome": nome, "codigo_barras": codigo_barras}
                imagem = _product_image(produto)
                self.assertIsNotNone(imagem)
                self.assertTrue(imagem.is_file())
                self.assertNotIn("coca", nome.casefold())


if __name__ == "__main__":
    unittest.main()