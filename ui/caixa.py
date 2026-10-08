from datetime import datetime
from decimal import Decimal
from html import escape
from pathlib import Path

import streamlit as st

from repositories.cliente_repository import ClienteRepository
from repositories.produto_repository import ProdutoRepository
from services.venda_service import VendaService
from utils.helpers import format_brl, money


CATEGORIES = ("Tudo", "Comida", "Bebida", "Higiene", "Limpeza")
CATEGORY_FILTERS = {
    "Tudo": "Todos",
    "Comida": "Alimentos",
    "Bebida": "Bebidas",
    "Higiene": "Higiene",
    "Limpeza": "Limpeza",
}
PAYMENT_LABELS = ("Dinheiro", "Cartao", "Pix", "Debito")
PAYMENT_METHOD_BY_LABEL = {
    "Dinheiro": "Dinheiro",
    "Cartao": "Cartao de credito",
    "Pix": "Pix",
    "Debito": "Cartao de debito",
}
PRODUCT_IMAGE_FILES = {
    "agua mineral - 500 ml": "01_agua_mineral_500ml.jpg",
    "refrigerante de cola - 350 ml": "02_coca_cola_350ml.jpg",
    "pao frances - unidade": "03_pao_frances_un.jpg",
    "leite integral - 1 l": "04_leite_integral_1l.jpg",
    "arroz tipo 1 - 5 kg": "05_arroz_5kg.jpg",
    "feijao carioca - 1 kg": "06_feijao_1kg.jpg",
    "detergente liquido - 500 ml": "07_detergente_500ml.jpg",
    "sabao em po - 1 kg": "08_sabao_po_1kg.jpg",
    "papel higienico - 4 unidades": "09_papel_higienico_4un.jpg",
    "cafe torrado - 500 g": "10_cafe_500g.jpg",
    "acucar refinado - 1 kg": "11_acucar_1kg.jpg",
    "oleo de soja - 900 ml": "12_oleo_soja_900ml.jpg",
    "macarrao - 500 g": "13_macarrao_500g.jpg",
    "molho de tomate - 340 g": "14_molho_tomate_340g.jpg",
    "farinha de trigo - 1 kg": "15_farinha_trigo_1kg.jpg",
    "margarina - 500 g": "16_margarina_500g.jpg",
    "sal refinado - 1 kg": "17_sal_1kg.jpg",
    "ovos - cartela": "18_ovos_cartela.jpg",
    "banana - kg": "19_banana_kg.jpg",
    "maca - kg": "20_maca_kg.jpg",
    "laranja - kg": "21_laranja_kg.jpg",
    "tomate - kg": "22_tomate_kg.jpg",
    "batata - kg": "23_batata_kg.jpg",
    "cenoura - kg": "24_cenoura_kg.jpg",
}


def _styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --pos-green: #00633f;
            --pos-green-dark: #004e33;
            --pos-mint: #e5f4ed;
            --pos-ink: #18231f;
            --pos-muted: #72807a;
            --pos-line: #e4ebe7;
            --pos-canvas: #f2f6f4;
        }
        [data-testid="stAppViewContainer"] { background: var(--pos-canvas); }
        [data-testid="stHeader"] { background: transparent; }
        .stMainBlockContainer { max-width: none; padding: .35rem .8rem 1rem; }
        .stApp:has(.st-key-pos_header) section[data-testid="stSidebar"] { display: none; }
        .st-key-pos_header {
            background: var(--pos-green);
            border-radius: 10px;
            color: #fff;
            padding: 6px 12px;
            margin-bottom: 10px;
        }
        .st-key-pos_header [data-testid="stMarkdownContainer"] p { color: #fff; margin: 0; }
        .st-key-pos_header [data-testid="stImage"] img {
            width: 88px;
            height: 88px;
            object-fit: contain;
        }
        .pos-operator { padding-top: 6px; line-height: 1.15; }
        .pos-operator strong { display: block; color: white; font-size: 13px; }
        .pos-operator small { color: #d0e8dc; font-size: 11px; }
        .pos-clock { padding-top: 3px; line-height: 1.1; text-align: center; }
        .pos-clock strong { display: block; color: #fff; font-size: 18px; font-weight: 800; }
        .pos-clock small { display: block; color: #fff; font-size: 15px; font-weight: 700; margin-top: 3px; }
        .st-key-pos_header [data-testid="stTextInput"] input {
            border: 0;
            background: #fff;
            color: var(--pos-ink);
            min-height: 38px;
        }
        .st-key-catalog_panel, .st-key-cart_panel, .st-key-payment_panel {
            background: #fff;
            border: 1px solid var(--pos-line);
            border-radius: 12px;
            padding: 12px;
        }
        .st-key-catalog_panel h3, .st-key-cart_panel h3, .st-key-payment_panel h3 {
            color: var(--pos-ink);
            font-size: 17px;
            line-height: 1.2;
            margin: 0 0 8px;
        }
        .st-key-nav_rail [data-testid="stButton"] button {
            min-height: 58px;
            padding: 5px 2px;
            font-size: 11px;
            border-color: transparent;
            background: transparent;
        }
        .st-key-nav_rail [data-testid="stButton"] button:hover,
        .st-key-nav_rail [data-testid="stButton"] button[kind="primary"] {
            color: var(--pos-green);
            background: var(--pos-mint);
            border-color: #c6e5d5;
        }
        .st-key-nav_rail [data-testid="stButton"] button p {
            white-space: nowrap;
            font-size: 9px;
        }
        [class*="st-key-product_card_"] {
            border: 1px solid var(--pos-line);
            border-radius: 8px;
            padding: 0;
            background: #fff;
            min-height: 0;
            text-align: center;
            overflow: hidden;
        }
        .product-image-placeholder {
            height: 160px;
            width: 100%;
            border-radius: 0;
            margin: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #91a69b;
            background: linear-gradient(145deg, #f1f7f3, #e6f1eb);
            border: 1px dashed #cbdcd2;
            font-size: 10px;
            font-weight: 650;
            overflow: hidden;
        }
        [class*="st-key-product_card_"] [data-testid="stImage"] {
            width: 100%;
            height: 160px;
            padding: 0;
            margin: 0;
            overflow: hidden;
        }
        [class*="st-key-product_card_"] img {
            height: 160px;
            width: 100%;
            object-fit: contain;
            border-radius: 0;
            margin: 0;
        }
        [class*="st-key-product_card_"] [data-testid="stMarkdownContainer"] p {
            font-size: 10px;
            line-height: 1.2;
            margin: 0;
            padding: 0 5px;
            color: var(--pos-ink);
            min-height: 22px;
            max-height: 22px;
            overflow: hidden;
        }
        [class*="st-key-product_card_"] [data-testid="stCaptionContainer"] {
            color: var(--pos-green);
            font-size: 11px;
            font-weight: 750;
            margin: 0;
            padding: 0 5px;
        }
        [class*="st-key-product_card_"] [data-testid="stButton"] button {
            min-height: 30px;
            height: 30px;
            padding: 2px 5px;
            border: 1px solid var(--pos-green);
            border-radius: 5px;
            color: #fff;
            background: var(--pos-green);
            font-size: 10px;
            font-weight: 700;
            white-space: nowrap;
        }
        [class*="st-key-product_card_"] [data-testid="stButton"] button p {
            color: #fff !important;
            font-size: 10px;
            line-height: 1;
            white-space: nowrap;
        }
        [class*="st-key-product_card_"] [data-testid="stButton"] button:hover {
            border-color: var(--pos-green-dark);
            background: var(--pos-green-dark);
        }
        .cart-line {
            border-bottom: 1px solid #e2ebe6;
            padding: 8px 2px 10px;
        }
        .cart-line-name { color: var(--pos-ink); font-size: 13px; font-weight: 700; line-height: 1.2; }
        .cart-line-meta { color: var(--pos-muted); font-size: 10px; margin-top: 3px; }
        [class*="st-key-cart_item_"] {
            background: #fbfdfc;
            border-radius: 7px;
            padding: 4px 7px;
            margin-bottom: 6px;
            border-bottom: 1px solid var(--pos-line);
        }
        [class*="st-key-cart_item_"] [data-testid="stButton"] button {
            min-height: 30px;
            height: 30px;
            padding: 0;
        }
        [class*="st-key-cart_item_"] [data-testid="stButton"] button p { display: none; }
        [class*="st-key-cart_item_"] [data-testid="stButton"] button[kind="secondary"] {
            background: #fff;
            border-color: #d9e4de;
            color: var(--pos-green-dark);
        }
        [class*="st-key-cart_item_"] [data-testid="stButton"] button p {
            display: block;
            color: var(--pos-green-dark) !important;
            font-size: 15px;
            line-height: 1;
            margin: 0;
        }
        .payment-total {
            position: relative;
            isolation: isolate;
            border-radius: 11px;
            padding: 2px;
            margin: 5px 0 12px;
            background: linear-gradient(110deg, #ff3158, #ffca3a, #47df91, #36b7ff, #a55cff, #ff3158);
            background-size: 300% 300%;
            animation: rgb-flow 5s linear infinite;
            box-shadow: 0 4px 14px rgba(0, 99, 63, .15);
        }
        .payment-total-inner {
            min-height: 102px;
            border-radius: 9px;
            padding: 13px 15px;
            color: #fff;
            background: linear-gradient(135deg, #064c34, #08764c);
            display: flex;
            flex-direction: column;
            justify-content: center;
            gap: 3px;
        }
        .payment-total-label {
            color: #c4e7d6;
            font-size: 13px;
            font-weight: 650;
        }
        .payment-total-amount {
            color: #fff;
            font-size: 42px;
            font-weight: 850;
            line-height: 1;
            font-variant-numeric: tabular-nums;
            white-space: nowrap;
        }
        .cart-total-highlight {
            border: 2px solid transparent;
            border-radius: 9px;
            padding: 1px;
            margin: 7px 0 12px;
            background: linear-gradient(#fff, #fff) padding-box,
                linear-gradient(110deg, #ff3158, #ffca3a, #47df91, #36b7ff, #a55cff, #ff3158) border-box;
            background-size: 100% 100%, 300% 300%;
            animation: rgb-flow 6s linear infinite;
        }
        .cart-total-inner {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 8px;
            padding: 8px 10px;
            color: #064c34;
            font-size: 13px;
            font-weight: 700;
        }
        .cart-total-inner strong {
            color: #064c34;
            font-size: 23px;
            font-weight: 850;
            white-space: nowrap;
            font-variant-numeric: tabular-nums;
        }
        @keyframes rgb-flow {
            0% { background-position: 0% 50%; }
            100% { background-position: 300% 50%; }
        }
        .change-box {
            background: var(--pos-mint);
            border-radius: 8px;
            color: var(--pos-green-dark);
            padding: 10px 12px;
            margin: 8px 0;
            font-size: 12px;
        }
        .st-key-payment_panel [data-testid="stButton"] button[kind="primary"] {
            background: var(--pos-green);
            border-color: var(--pos-green);
            min-height: 44px;
        }
        .st-key-payment_panel .st-key-finalize_sale button {
            min-height: 54px;
            border: 2px solid transparent;
            border-radius: 9px;
            color: #fff;
            font-size: 14px;
            font-weight: 750;
            background:
                linear-gradient(115deg, #005b39, #087d50) padding-box,
                linear-gradient(110deg, #ff3158, #ffca3a, #47df91, #36b7ff, #a55cff, #ff3158) border-box;
            background-size: 100% 100%, 300% 300%;
            animation: rgb-flow 5s linear infinite;
            box-shadow: 0 5px 16px rgba(0, 99, 63, .22);
            transition: transform .15s ease, box-shadow .15s ease;
        }
        .st-key-payment_panel .st-key-finalize_sale button:hover:not(:disabled) {
            transform: translateY(-1px);
            box-shadow: 0 7px 20px rgba(0, 99, 63, .3);
        }
        .st-key-payment_panel .st-key-finalize_sale button:disabled {
            opacity: .52;
            animation: none;
        }
        .st-key-payment_choices [data-testid="stButton"] button {
            min-height: 39px;
            padding: 3px 0;
        }
        .st-key-payment_choices [data-testid="stButton"] button p { display: none; }
        .st-key-payment_choices [data-testid="stCaptionContainer"] {
            text-align: center;
            font-size: 10px;
            white-space: nowrap;
            margin-top: -5px;
        }
        @media (max-width: 900px) {
            .stMainBlockContainer { padding: .25rem .45rem .75rem; }
            .st-key-pos_header { padding-left: 7px; padding-right: 7px; }
            .st-key-catalog_panel, .st-key-cart_panel, .st-key-payment_panel { padding: 9px; }
        }
        @media (prefers-reduced-motion: reduce) {
            .payment-total,
            .cart-total-highlight,
            .st-key-payment_panel .st-key-finalize_sale button {
                animation: none;
            }
            .st-key-payment_panel .st-key-finalize_sale button { transition: none; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _category(product: dict) -> str:
    name = product["nome"].casefold()
    if any(word in name for word in ("agua", "leite", "suco", "refrigerante", "cafe")):
        return "Bebidas"
    if any(word in name for word in ("papel", "sabonete", "shampoo", "higien")):
        return "Higiene"
    if any(word in name for word in ("detergente", "sabao", "limpeza", "amaciante")):
        return "Limpeza"
    return "Alimentos"


def _product_image(product: dict) -> Path | None:
    image_directory = Path(__file__).resolve().parents[1] / "assets" / "products"
    cropped_directory = image_directory / "cropped"
    mapped_image = PRODUCT_IMAGE_FILES.get(product["nome"].casefold())
    if mapped_image:
        cropped_candidate = cropped_directory / mapped_image
        if cropped_candidate.is_file():
            return cropped_candidate
        candidate = image_directory / mapped_image
        if candidate.is_file():
            return candidate
    stems = [str(product["id"])]
    if product.get("codigo_barras"):
        stems.insert(0, Path(str(product["codigo_barras"])).name)
    for stem in stems:
        for extension in (".png", ".jpg", ".jpeg", ".webp"):
            filename = f"{stem}{extension}"
            for directory in (cropped_directory, image_directory):
                candidate = directory / filename
                if candidate.is_file():
                    return candidate
    return None


def _add_to_cart(product_id: int) -> None:
    cart = st.session_state.setdefault("carrinho", {})
    cart[product_id] = cart.get(product_id, 0) + 1


def _scan_barcode() -> None:
    barcode = str(st.session_state.get("pos_search", "")).strip()
    if not barcode:
        return

    product = ProdutoRepository().buscar_por_codigo(barcode)
    if product is None:
        st.session_state["barcode_feedback"] = ("info", f"Código {barcode} não encontrado. Busca mantida no catálogo.")
        return

    cart = st.session_state.setdefault("carrinho", {})
    current_quantity = cart.get(product["id"], 0)
    if current_quantity >= product["estoque"]:
        st.session_state["barcode_feedback"] = ("warning", f"Estoque insuficiente para {product['nome']}.")
    else:
        cart[product["id"]] = current_quantity + 1
        st.session_state["barcode_feedback"] = ("success", f"{product['nome']} adicionado ao carrinho.")
        st.session_state["pos_search"] = ""


def _remove_from_cart(product_id: int) -> None:
    cart = st.session_state.get("carrinho", {})
    cart.pop(product_id, None)


def _change_quantity(product_id: int, change: int) -> None:
    cart = st.session_state.get("carrinho", {})
    quantity = cart.get(product_id, 0) + change
    product = ProdutoRepository().buscar_por_id(product_id)
    if product is not None and quantity > product["estoque"]:
        return
    if quantity <= 0:
        cart.pop(product_id, None)
    else:
        cart[product_id] = quantity


def _cancel_sale() -> None:
    st.session_state["carrinho"] = {}
    st.session_state["sale_context"] = st.session_state.get("sale_context", 0) + 1


def _set_page(page: str) -> None:
    st.session_state["pagina"] = page


def render() -> None:
    _styles()
    repository = ProdutoRepository()
    produtos = repository.listar()
    if "carrinho" not in st.session_state:
        st.session_state.carrinho = {}
    if "sale_context" not in st.session_state:
        st.session_state.sale_context = 0
    sale_context = st.session_state.sale_context

    with st.container(key="pos_header"):
        brand, search, operator, clock = st.columns([1.2, 5.1, 1.45, 1.1], vertical_alignment="center")
        with brand:
            logo_path = Path(__file__).resolve().parents[1] / "assets" / "Logo Atualizado.png"
            st.image(str(logo_path), width=88)
        with search:
            search_term = st.text_input(
                "Buscar produto por nome ou código de barras",
                placeholder="Bipe o código de barras e pressione Enter, ou busque pelo nome...",
                key="pos_search",
                label_visibility="collapsed",
                on_change=_scan_barcode,
            )
        with operator:
            st.markdown('<div class="pos-operator"><strong>Operador</strong><small>Caixa local</small></div>', unsafe_allow_html=True)
        with clock:
            now = datetime.now().astimezone()
            st.markdown(f'<div class="pos-clock"><strong>{now:%d/%m/%Y}</strong><small>{now:%H:%M}</small></div>', unsafe_allow_html=True)
    nav, catalog_col, cart_col, payment_col = st.columns([0.075, 0.32, 0.39, 0.215], gap="small", vertical_alignment="top")
    barcode_feedback = st.session_state.pop("barcode_feedback", None)
    if barcode_feedback:
        level, message = barcode_feedback
        if level == "success":
            st.toast(message, icon=":material/check_circle:")
        elif level == "warning":
            st.warning(message)
        else:
            st.info(message)

    with nav:
        with st.container(key="nav_rail"):
            st.button("Caixa", icon=":material/point_of_sale:", type="primary", width="stretch", disabled=True)
            st.button("Produtos", icon=":material/inventory_2:", width="stretch", on_click=_set_page, args=("Produtos",))
            st.button("Estoque", icon=":material/warehouse:", width="stretch", on_click=_set_page, args=("Estoque",))
            st.button("Relatórios", icon=":material/analytics:", width="stretch", on_click=_set_page, args=("Dashboard",))

    with catalog_col:
        with st.container(key="catalog_panel", border=True, height=680):
            title, view_all = st.columns([1, 0.6], vertical_alignment="center")
            title.subheader("Produtos")
            view_all.button("Ver todos", icon=":material/arrow_forward:", width="stretch", on_click=lambda: st.session_state.update(pagina="Produtos"))
            category = st.segmented_control("Categorias", CATEGORIES, default="Tudo", label_visibility="collapsed", key="pos_category")
            category = CATEGORY_FILTERS.get(category or "Tudo", "Todos")

            term = (search_term or "").strip().casefold()
            visible_products = [
                product for product in produtos
                if product["estoque"] > 0
                and (category == "Todos" or _category(product) == category)
                and (not term or term in product["nome"].casefold() or term in (product["codigo_barras"] or "").casefold())
            ]
            if visible_products:
                for offset in range(0, len(visible_products), 3):
                    product_columns = st.columns(3, gap="small")
                    for column, product in zip(product_columns, visible_products[offset:offset + 3]):
                        with column:
                            with st.container(key=f"product_card_{product['id']}"):
                                image_path = _product_image(product)
                                if image_path:
                                    st.image(str(image_path), width="stretch")
                                else:
                                    st.markdown('<div class="product-image-placeholder">IMAGEM DO PRODUTO</div>', unsafe_allow_html=True)
                                st.markdown(product["nome"])
                                st.caption(format_brl(product["preco"]))
                                if st.button(
                                    "Adicionar",
                                    key=f"add_product_{product['id']}",
                                    help=f"Adicionar {product['nome']} ao carrinho",
                                    width="stretch",
                                ):
                                    _add_to_cart(product["id"])
                                    st.rerun()
            else:
                st.caption("Nenhum produto corresponde à busca.")

    with cart_col:
        with st.container(key="cart_panel", border=True, height=680):
            cart_title, clear_cart = st.columns([1, 0.45], vertical_alignment="center")
            cart_title.subheader("Carrinho de compras")
            clear_cart.button("Limpar", icon=":material/delete:", width="stretch", on_click=_cancel_sale)

            cart = st.session_state.carrinho
            product_by_id = {product["id"]: product for product in produtos}
            available_cart = {
                product_id: quantity
                for product_id, quantity in cart.items()
                if product_id in product_by_id
            }
            if not available_cart:
                st.markdown("<div class='cart-empty'>Seu carrinho está vazio.<br>Selecione produtos para iniciar uma venda.</div>", unsafe_allow_html=True)
            else:
                for product_id, quantity in list(available_cart.items()):
                    product = product_by_id[product_id]
                    item_total = money(product["preco"]) * quantity
                    with st.container(key=f"cart_item_{product_id}"):
                        name_col, qty_col, total_col, delete_col = st.columns([0.45, 0.29, 0.18, 0.08], vertical_alignment="center")
                        with name_col:
                            product_name = escape(product["nome"])
                            st.markdown(f'<div class="cart-line-name">{product_name}</div><div class="cart-line-meta">{format_brl(product["preco"])} cada</div>', unsafe_allow_html=True)
                        with qty_col:
                            qty_buttons = st.columns([1, 0.8, 1], gap="small", vertical_alignment="center")
                            qty_buttons[0].button("−", key=f"qty_minus_{product_id}", on_click=_change_quantity, args=(product_id, -1), help="Diminuir quantidade")
                            qty_buttons[1].markdown(f"<div style='text-align:center;padding-top:5px;font-size:13px;font-weight:750'>{quantity}</div>", unsafe_allow_html=True)
                            qty_buttons[2].button("+", key=f"qty_plus_{product_id}", on_click=_change_quantity, args=(product_id, 1), disabled=quantity >= product["estoque"], help="Aumentar quantidade")
                        with total_col:
                            st.markdown(f"<div style='text-align:right;font-size:14px;font-weight:750'>{format_brl(item_total)}</div>", unsafe_allow_html=True)
                        with delete_col:
                            st.button("×", key=f"remove_{product_id}", on_click=_remove_from_cart, args=(product_id,), help="Remover produto")

            subtotal = money(sum(
                (money(product_by_id[product_id]["preco"]) * quantity for product_id, quantity in available_cart.items()),
                Decimal("0.00"),
            ))
            st.markdown("<div class='cart-divider'></div>", unsafe_allow_html=True)

            discount_mode = st.segmented_control(
                "Tipo de desconto", ["R$", "%"], default="R$", key=f"discount_mode_{sale_context}", label_visibility="collapsed"
            ) or "R$"
            if discount_mode == "%":
                discount_percent = st.number_input("Desconto (%)", min_value=0.0, max_value=100.0, value=0.0, step=1.0, key=f"discount_percent_{sale_context}")
                discount_amount = money(subtotal * Decimal(str(discount_percent)) / Decimal("100"))
            else:
                discount_amount_input = st.number_input("Desconto (R$)", min_value=0.0, max_value=float(subtotal), value=0.0, step=1.0, key=f"discount_real_{sale_context}")
                discount_amount = money(discount_amount_input)
            total = money(max(Decimal("0.00"), subtotal - discount_amount))

            summary_subtotal, summary_discount = st.columns([1, 1])
            summary_subtotal.caption(f"Subtotal  {format_brl(subtotal)}")
            summary_discount.caption(f"Desconto  {format_brl(discount_amount)}")
            st.markdown(
                f"<div class='cart-total-highlight'><div class='cart-total-inner'>Total da venda <strong>{format_brl(total)}</strong></div></div>",
                unsafe_allow_html=True,
            )

            save_col, cancel_col = st.columns(2, gap="small")
            save_col.button(
                "Salvar orçamento",
                icon=":material/description:",
                width="stretch",
                disabled=not available_cart,
                on_click=lambda: st.session_state.update(orcamento=dict(available_cart)),
            )
            cancel_col.button("Cancelar venda", icon=":material/close:", width="stretch", on_click=_cancel_sale)

    with payment_col:
        with st.container(key="payment_panel", border=True, height=680):
            st.subheader("Pagamento")
            st.markdown(
                f"<div class='payment-total'><div class='payment-total-inner'><span class='payment-total-label'>TOTAL A PAGAR</span><strong class='payment-total-amount'>{format_brl(total)}</strong></div></div>",
                unsafe_allow_html=True,
            )
            payment_key = f"payment_method_{sale_context}"
            if payment_key not in st.session_state:
                st.session_state[payment_key] = "Dinheiro"
            with st.container(key="payment_choices"):
                payment_columns = st.columns(4, gap="small")
                payment_buttons = (
                    (payment_columns[0], "Dinheiro", ":material/payments:"),
                    (payment_columns[1], "Cartao", ":material/credit_card:"),
                    (payment_columns[2], "Pix", ":material/qr_code_2:"),
                    (payment_columns[3], "Debito", ":material/credit_score:"),
                )
                for payment_column, label, icon in payment_buttons:
                    if payment_column.button(
                        label,
                        icon=icon,
                        key=f"{payment_key}_{label}",
                        help=label,
                        type="primary" if st.session_state[payment_key] == label else "secondary",
                        width="stretch",
                    ):
                        st.session_state[payment_key] = label
                        st.rerun()
                    payment_column.caption(label)
            payment_label = st.session_state[payment_key]
            payment_method = PAYMENT_METHOD_BY_LABEL[payment_label]
            received = None
            change = Decimal("0.00")
            if payment_label == "Dinheiro":
                due = float(total)
                received_key = f"received_{sale_context}"
                if received_key not in st.session_state:
                    st.session_state[received_key] = due
                received = st.number_input("Valor recebido", min_value=0.0, step=1.0, key=received_key)
                change = money(Decimal(str(received)) - total)
                if change >= 0:
                    st.markdown(f"<div class='change-box'>Troco <strong>{format_brl(change)}</strong></div>", unsafe_allow_html=True)
                else:
                    st.warning("Valor recebido abaixo do total.")
            elif payment_label == "Cartao":
                st.caption("Pagamento no crédito")
            elif payment_label == "Debito":
                st.caption("Pagamento no débito")
            else:
                st.caption("Pagamento via Pix")

            clients = ClienteRepository().listar()
            client_options = [None, *[client["id"] for client in clients]]
            client_by_id = {client["id"]: client for client in clients}
            cliente_id = st.selectbox(
                "Cliente (opcional)",
                options=client_options,
                format_func=lambda value: "Sem cliente" if value is None else client_by_id[value]["nome"],
                key=f"customer_{sale_context}",
            )
            finalize = st.button(
                "Finalizar venda (F1)",
                type="primary",
                icon=":material/check_circle:",
                width="stretch",
                disabled=not available_cart,
                key="finalize_sale",
            )
            if finalize:
                try:
                    result = VendaService().finalizar_venda(
                        [{"produto_id": product_id, "quantidade": quantity} for product_id, quantity in available_cart.items()],
                        forma_pagamento=payment_method,
                        desconto=discount_amount,
                        valor_recebido=received,
                        cliente_id=cliente_id,
                    )
                except ValueError as error:
                    st.error(str(error))
                else:
                    st.session_state.carrinho = {}
                    st.session_state.sale_context += 1
                    st.success(f"Venda #{result['venda_id']} concluída. Total {format_brl(result['total'])}.")
                    st.rerun()

