import streamlit as st

from repositories.produto_repository import ProdutoRepository
from utils.helpers import format_brl
from utils.validators import validate_product


def render() -> None:
    st.title("Produtos")
    repository = ProdutoRepository()
    with st.expander("Catalogo de demonstracao"):
        if st.button("Adicionar 24 produtos de exemplo", icon=":material/inventory_2:"):
            inseridos = repository.criar_produtos_demo()
            if inseridos:
                st.success(f"{inseridos} produto(s) de demonstracao adicionado(s).")
            else:
                st.info("Os produtos de demonstracao ja existem.")

    with st.expander("Cadastrar produto", expanded=True):
        with st.form("novo_produto", clear_on_submit=True):
            nome = st.text_input("Nome")
            codigo = st.text_input("Codigo de barras", help="Opcional e unico")
            preco = st.number_input("Preco (R$)", min_value=0.0, step=0.5, format="%.2f")
            estoque = st.number_input("Estoque inicial", min_value=0, step=1)
            minimo = st.number_input("Estoque minimo", min_value=0, step=1)
            salvar = st.form_submit_button("Salvar produto", type="primary")
        if salvar:
            try:
                validate_product(nome, preco, estoque, minimo)
                repository.criar(nome, preco, estoque, minimo, codigo)
            except ValueError as error:
                st.error(str(error))
            else:
                st.success("Produto cadastrado.")
                st.rerun()

    produtos = repository.listar(ativos=None)
    if produtos:
        st.subheader("Catalogo")
        st.dataframe(
            [
                {"Codigo": p["codigo_barras"] or "-", "Produto": p["nome"], "Preco": format_brl(p["preco"]), "Estoque": p["estoque"], "Minimo": p["estoque_minimo"], "Status": "Ativo" if p["ativo"] else "Inativo"}
                for p in produtos
            ],
            width="stretch",
            hide_index=True,
        )
        ativos = [p for p in produtos if p["ativo"]]
        if ativos:
            st.subheader("Editar cadastro")
            por_id = {p["id"]: p for p in ativos}
            selecionado = st.selectbox("Produto para editar", options=list(por_id), format_func=lambda value: por_id[value]["nome"])
            produto = por_id[selecionado]
            with st.form("editar_produto"):
                nome_editado = st.text_input("Nome", value=produto["nome"])
                codigo_editado = st.text_input("Codigo de barras", value=produto["codigo_barras"] or "")
                preco_editado = st.number_input("Preco (R$)", min_value=0.0, value=float(produto["preco"]), step=0.5, format="%.2f")
                minimo_editado = st.number_input("Estoque minimo", min_value=0, value=int(produto["estoque_minimo"]), step=1)
                salvar_edicao = st.form_submit_button("Salvar alteracoes")
            if salvar_edicao:
                try:
                    validate_product(nome_editado, preco_editado, produto["estoque"], minimo_editado)
                    repository.atualizar(selecionado, nome_editado, preco_editado, minimo_editado, codigo_editado)
                except ValueError as error:
                    st.error(str(error))
                else:
                    st.success("Cadastro atualizado.")
                    st.rerun()
            if st.button("Desativar produto", icon=":material/block:"):
                repository.desativar(selecionado)
                st.rerun()
