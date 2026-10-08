# Caixa Registradora

Aplicacao local de ponto de venda com interface Streamlit, persistencia SQLite e separacao entre interface, servicos e repositories.

## Recursos

- Cadastro, edicao e desativacao de produtos.
- Catalogo de demonstracao com 24 produtos, carregado automaticamente sem duplicar produtos existentes.
- Carrinho com calculo de subtotal, desconto em reais e troco para pagamentos em dinheiro.
- Pagamento por dinheiro, Pix, cartao de credito ou debito.
- Gravacao atomica da venda, dos itens e da baixa de estoque.
- Ajustes manuais de estoque e alertas de estoque minimo.
- Indicadores diarios e consulta de vendas recentes.

## Executar

No terminal, entre nesta pasta e execute:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

O projeto usa sempre a porta `8501`, definida em `.streamlit/config.toml`. Mantenha essa instância aberta durante as atualizacoes: o Streamlit recarrega os arquivos automaticamente. Para reiniciar, pare a instancia atual com `Ctrl+C` e execute novamente o mesmo comando; nao inicie outra instancia em uma porta diferente.

O banco `database/caixa.db` e as tabelas sao criados automaticamente na primeira inicializacao. Os testes usam bancos temporarios e podem ser executados com:

```powershell
python -m unittest discover -s tests -v
```

As vendas aceitam `usuario_id` e `cliente_id`, mas esta primeira versao ainda nao inclui tela de autenticacao nem cadastro de operadores/clientes.

## Imagens dos produtos

As 24 imagens demonstrativas estao em `assets/products/` e associadas individualmente aos produtos. O cadastro usa descricoes genericas, mesmo quando a embalagem da imagem exibe uma marca. Para imagens de outros produtos, use o codigo de barras ou o ID como nome do arquivo (por exemplo, `7890000000000.jpg` ou `1.png`). Enquanto nao houver imagem correspondente, o caixa mostra um placeholder.
