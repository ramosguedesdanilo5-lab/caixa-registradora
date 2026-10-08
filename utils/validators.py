import re
from decimal import Decimal

from utils.helpers import money


def validate_product(nome: str, preco: Decimal | float, estoque: int, estoque_minimo: int) -> None:
    if not nome.strip():
        raise ValueError("Informe o nome do produto.")
    if money(preco) < 0:
        raise ValueError("O preco nao pode ser negativo.")
    if estoque < 0 or estoque_minimo < 0:
        raise ValueError("Estoque e estoque minimo nao podem ser negativos.")


def validate_cpf(cpf: str | None) -> str | None:
    if cpf is None or not cpf.strip():
        return None
    digits = re.sub(r"\D", "", cpf)
    if len(digits) != 11 or len(set(digits)) == 1:
        raise ValueError("CPF invalido: informe 11 digitos.")
    return digits
