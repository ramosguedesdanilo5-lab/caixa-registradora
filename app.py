import streamlit as st

from database.connection import initialize_database
from repositories.produto_repository import ProdutoRepository
from ui import caixa, dashboard, estoque, produtos

st.set_page_config(page_title="Caixa Registradora", page_icon=":material/storefront:", layout="wide")
initialize_database()
ProdutoRepository().criar_produtos_demo()

if "pagina" not in st.session_state:
    st.session_state.pagina = "Caixa"

pagina = st.session_state.pagina
if pagina == "Caixa":
    caixa.render()
    st.stop()

st.sidebar.title("Caixa Registradora")
pagina = st.sidebar.radio(
    "Menu",
    ["Caixa", "Dashboard", "Produtos", "Estoque"],
    index=["Caixa", "Dashboard", "Produtos", "Estoque"].index(pagina),
    label_visibility="collapsed",
)
st.session_state.pagina = pagina

if pagina == "Dashboard":
    dashboard.render()
elif pagina == "Produtos":
    produtos.render()
elif pagina == "Estoque":
    estoque.render()
else:
    caixa.render()
