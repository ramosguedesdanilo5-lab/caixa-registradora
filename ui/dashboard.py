from datetime import date, timedelta

import pandas as pd
import streamlit as st

from repositories.produto_repository import ProdutoRepository
from services.relatorio_service import RelatorioService
from utils.helpers import format_brl


def render() -> None:
    st.title("Resumo de operacao")
    relatorios = RelatorioService()
    resumo = relatorios.resumo_hoje()
    produtos = ProdutoRepository().listar()
    baixos = [p for p in produtos if p["estoque"] <= p["estoque_minimo"]]
    col_vendas, col_faturamento, col_repor = st.columns(3)
    col_vendas.metric("Vendas hoje", resumo["quantidade_vendas"])
    col_faturamento.metric("Faturamento hoje", format_brl(resumo["faturamento"]))
    col_repor.metric("Produtos para repor", len(baixos))

    st.subheader("Vendas recentes")
    inicio = date.today() - timedelta(days=6)
    vendas = relatorios.vendas_no_periodo(inicio, date.today())
    if vendas:
        st.dataframe(
            pd.DataFrame([
                {"Venda": f"#{v['id']}", "Data": v["data_hora"].replace("T", " "), "Itens": v["quantidade_itens"], "Pagamento": v["forma_pagamento"], "Total": format_brl(v["total"])}
                for v in vendas
            ]),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.caption("Nenhuma venda registrada nos ultimos sete dias.")
    if baixos:
        st.subheader("Estoque baixo")
        st.dataframe(
            [{"Produto": p["nome"], "Disponivel": p["estoque"], "Minimo": p["estoque_minimo"]} for p in baixos],
            use_container_width=True,
            hide_index=True,
        )
