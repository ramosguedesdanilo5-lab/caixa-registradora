from dataclasses import dataclass


@dataclass(frozen=True)
class Usuario:
    id: int
    nome: str
    login: str
    nivel_acesso: str
    ativo: bool = True
