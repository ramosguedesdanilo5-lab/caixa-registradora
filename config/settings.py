from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "database" / "caixa.db"
CURRENCY = "BRL"
PAYMENT_METHODS = ("Dinheiro", "Pix", "Cartao de credito", "Cartao de debito")
MAX_DISCOUNT_PERCENT = 100.0
