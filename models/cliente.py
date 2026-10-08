from dataclasses import dataclass


@dataclass(frozen=True)
class Cliente:
    id: int
    nome: str
    cpf: str | None = None
    telefone: str | None = None
    ativo: bool = True
