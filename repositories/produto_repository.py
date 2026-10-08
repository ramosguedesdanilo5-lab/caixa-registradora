import sqlite3
from pathlib import Path
from typing import Any

from config.settings import DATABASE_PATH
from database.connection import get_connection


class ProdutoRepository:
    DEMO_PRODUCTS = (
        ("Agua mineral - 500 ml", 3.49, 30, 10, "DEMO-100008"),
        ("Refrigerante de cola - 350 ml", 5.00, 20, 6, "DEMO-100009"),
        ("Pao frances - unidade", 0.75, 40, 10, "DEMO-100010"),
        ("Leite integral - 1 L", 5.79, 24, 8, "DEMO-100003"),
        ("Arroz tipo 1 - 5 kg", 28.90, 18, 5, "DEMO-100001"),
        ("Feijao carioca - 1 kg", 8.49, 5, 6, "DEMO-100002"),
        ("Detergente liquido - 500 ml", 2.80, 20, 6, "DEMO-100011"),
        ("Sabao em po - 1 kg", 12.90, 18, 5, "DEMO-100012"),
        ("Papel higienico - 4 unidades", 6.90, 18, 5, "DEMO-100013"),
        ("Cafe torrado - 500 g", 18.90, 4, 4, "DEMO-100004"),
        ("Acucar refinado - 1 kg", 4.99, 22, 5, "DEMO-100005"),
        ("Oleo de soja - 900 ml", 7.49, 16, 5, "DEMO-100006"),
        ("Macarrao - 500 g", 4.59, 2, 5, "DEMO-100007"),
        ("Molho de tomate - 340 g", 3.49, 18, 5, "DEMO-100014"),
        ("Farinha de trigo - 1 kg", 5.49, 12, 4, "DEMO-100015"),
        ("Margarina - 500 g", 7.90, 16, 4, "DEMO-100016"),
        ("Sal refinado - 1 kg", 2.49, 20, 5, "DEMO-100017"),
        ("Ovos - cartela", 18.90, 10, 4, "DEMO-100018"),
        ("Banana - kg", 5.99, 15, 5, "DEMO-100019"),
        ("Maca - kg", 9.90, 12, 4, "DEMO-100020"),
        ("Laranja - kg", 4.99, 18, 5, "DEMO-100021"),
        ("Tomate - kg", 7.99, 14, 5, "DEMO-100022"),
        ("Batata - kg", 5.49, 16, 5, "DEMO-100023"),
        ("Cenoura - kg", 6.99, 13, 4, "DEMO-100024"),
    )

    def __init__(self, database_path: str | Path = DATABASE_PATH):
        self.database_path = database_path

    def criar_produtos_demo(self) -> int:
        connection = get_connection(self.database_path)
        try:
            changes_before = connection.total_changes
            connection.executemany(
                """INSERT INTO produtos (nome, preco, estoque, estoque_minimo, codigo_barras)
                   VALUES (?, ?, ?, ?, ?)
                   ON CONFLICT(codigo_barras) DO NOTHING""",
                self.DEMO_PRODUCTS,
            )
            inserted = connection.total_changes - changes_before
            connection.executemany(
                "UPDATE produtos SET nome = ? WHERE codigo_barras = ? AND nome <> ?",
                [(nome, codigo, nome) for nome, _, _, _, codigo in self.DEMO_PRODUCTS],
            )
            connection.commit()
            return inserted
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def listar(self, ativos: bool | None = True) -> list[dict[str, Any]]:
        connection = get_connection(self.database_path)
        try:
            query = "SELECT * FROM produtos"
            parameters: tuple[Any, ...] = ()
            if ativos is not None:
                query += " WHERE ativo = ?"
                parameters = (int(ativos),)
            query += " ORDER BY nome COLLATE NOCASE"
            return [dict(row) for row in connection.execute(query, parameters)]
        finally:
            connection.close()

    def buscar_por_id(self, produto_id: int, connection: sqlite3.Connection | None = None):
        owns_connection = connection is None
        connection = connection or get_connection(self.database_path)
        try:
            row = connection.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,)).fetchone()
            return dict(row) if row else None
        finally:
            if owns_connection:
                connection.close()

    def buscar_por_codigo(self, codigo_barras: str) -> dict[str, Any] | None:
        connection = get_connection(self.database_path)
        try:
            row = connection.execute(
                "SELECT * FROM produtos WHERE codigo_barras = ? AND ativo = 1", (codigo_barras,)
            ).fetchone()
            return dict(row) if row else None
        finally:
            connection.close()

    def criar(self, nome: str, preco: float, estoque: int, estoque_minimo: int, codigo_barras: str | None = None) -> int:
        connection = get_connection(self.database_path)
        try:
            cursor = connection.execute(
                "INSERT INTO produtos (nome, preco, estoque, estoque_minimo, codigo_barras) VALUES (?, ?, ?, ?, ?)",
                (nome.strip(), preco, estoque, estoque_minimo, codigo_barras or None),
            )
            connection.commit()
            return int(cursor.lastrowid)
        except sqlite3.IntegrityError as error:
            connection.rollback()
            raise ValueError("Ja existe um produto com esse codigo de barras.") from error
        finally:
            connection.close()

    def atualizar(self, produto_id: int, nome: str, preco: float, estoque_minimo: int, codigo_barras: str | None) -> None:
        connection = get_connection(self.database_path)
        try:
            cursor = connection.execute(
                "UPDATE produtos SET nome = ?, preco = ?, estoque_minimo = ?, codigo_barras = ? WHERE id = ?",
                (nome.strip(), preco, estoque_minimo, codigo_barras or None, produto_id),
            )
            if cursor.rowcount == 0:
                raise ValueError("Produto nao encontrado.")
            connection.commit()
        except sqlite3.IntegrityError as error:
            connection.rollback()
            raise ValueError("Ja existe um produto com esse codigo de barras.") from error
        finally:
            connection.close()

    def desativar(self, produto_id: int) -> None:
        connection = get_connection(self.database_path)
        try:
            connection.execute("UPDATE produtos SET ativo = 0 WHERE id = ?", (produto_id,))
            connection.commit()
        finally:
            connection.close()
