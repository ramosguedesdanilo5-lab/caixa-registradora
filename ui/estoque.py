import streamlit as st

from repositories.produto_repository import ProdutoRepository
from services.estoque_service import EstoqueService


def render() -> None:
    st.title("Estoque")
    repository = ProdutoRepository()
    produtos = repository.listar()
    baixos = EstoqueService().produtos_com_estoque_baixo()
    if baixos:
        st.warning(f"{len(baixos)} produto(s) no limite ou abaixo do estoque minimo.")
    if produtos:
        st.dataframe(
            [{"Produto": p["nome"], "Estoque atual": p["estoque"], "Estoque minimo": p["estoque_minimo"], "Situacao": "Repor" if p in baixos else "Normal"} for p in produtos],
            use_container_width=True,
            hide_index=True,
        )
        st.subheader("Ajuste manual")
        por_id = {p["id"]: p for p in produtos}
        produto_id = st.selectbox("Produto", options=list(por_id), format_func=lambda value: por_id[value]["nome"])
        delta = st.number_input("Variacao de unidades", value=1, step=1, help="Use valor positivo para entrada e negativo para saida")
        if st.button("Aplicar ajuste", type="primary"):
            try:
                EstoqueService().ajustar(produto_id, delta)
            except ValueError as error:
                st.error(str(error))
            else:
                st.success("Estoque atualizado.")
                st.rerun()
    else:
        st.info("Ainda nao ha produtos cadastrados.")
