from datetime import date
from decimal import Decimal
from pathlib import Path

from config.settings import DATABASE_PATH
from database.connection import get_connection
from repositories.venda_repository import VendaRepository
from utils.helpers import money


class RelatorioService:
    def __init__(self, database_path: str | Path = DATABASE_PATH, venda_repository: VendaRepository | None = None):
        self.database_path = database_path
        self.vendas = venda_repository or VendaRepository(database_path)

    def resumo_hoje(self) -> dict:
        return self.vendas.resumo_hoje()

    def vendas_no_periodo(self, inicio: date, fim: date) -> list[dict]:
        connection = get_connection(self.database_path)
        try:
            rows = connection.execute(
                """SELECT v.*, COUNT(i.id) AS quantidade_itens FROM vendas v
                   LEFT JOIN itens_venda i ON i.venda_id = v.id
                   WHERE date(v.data_hora) BETWEEN ? AND ?
                   GROUP BY v.id ORDER BY v.data_hora DESC""",
                (inicio.isoformat(), fim.isoformat()),
            )
            return [dict(row) for row in rows]
        finally:
            connection.close()

    def faturamento_no_periodo(self, inicio: date, fim: date) -> Decimal:
        vendas = self.vendas_no_periodo(inicio, fim)
        return money(sum((Decimal(str(venda["total"])) for venda in vendas), Decimal("0.00")))
