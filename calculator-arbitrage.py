import streamlit as st
import requests

# Configuración de la página (Título en la pestaña del navegador)
st.set_page_config(page_title="Calculadora Cripto & P2P", page_icon="📊", layout="centered")

# -------------------------------------------------------------------
# LÓGICA DE NEGOCIO (Tus funciones matemáticas)
# -------------------------------------------------------------------
def obtener_precio_binance(symbol="BTCUSDT"):
    symbol = symbol.upper().strip()
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return float(response.json()['price'])
        return None
    except Exception:
        return None

def convert_crypto(amount, price_a, price_b):
    if price_b == 0: return 0
    return (amount * price_a) / price_b

def porcentaje_cambio(valor_inicial, valor_final):
    if valor_inicial == 0: return 0
    return ((valor_final - valor_inicial) / abs(valor_inicial)) * 100

def calcular_p2p_profit(amount, buy_price, sell_price, buy_fee_pct=0.0, sell_fee_pct=0.0):
    buy_fee = buy_fee_pct / 100
    sell_fee = sell_fee_pct / 100
    total_cost = amount * buy_price * (1 + buy_fee)
    revenue = amount * sell_price * (1 - sell_fee)
    profit = revenue - total_cost
    profit_pct = (profit / total_cost) * 100 if total_cost != 0 else 0.0
    break_even_price = (buy_price * (1 + buy_fee)) / (1 - sell_fee) if (1 - sell_fee) != 0 else 0.0
    p2p_margin_pct = ((sell_price - buy_price) / buy_price) * 100 if buy_price != 0 else 0.0

    return {
        "total_cost": total_cost, "total_revenue": revenue, "profit": profit,
        "profit_pct": profit_pct, "break_even_price": break_even_price, "p2p_margin_pct": p2p_margin_pct
    }

# -------------------------------------------------------------------
# INTERFAZ GRÁFICA (Streamlit)
# -------------------------------------------------------------------
st.title("📊 Calculadora Cripto & P2P")
st.write("Herramienta de análisis financiero para arbitraje y conversiones.")

# Creamos pestañas visuales para navegar en la app de forma moderna
tab1, tab2, tab3 = st.tabs(["🔄 Conversión & API", "💸 Margen P2P", "📈 % de Cambio"])

# --- PESTAÑA 1: CONVERSIÓN ---
with tab1:
    st.header("Conversor de Monedas")
    amount = st.number_input("Cantidad de cripto A a cambiar", min_value=0.0, value=1.0, step=0.1, key="conv_amount")

    usar_api = st.checkbox("Obtener precio real desde Binance API", value=True)

    if usar_api:
        par = st.text_input("Introduce el par de Binance (Ej: BTCUSDT, ETHUSDT)", value="BTCUSDT")
        price_a = obtener_precio_binance(par)
        if price_a:
            st.info(f"Precio actual de mercado para {par.upper()}: **{price_a:,} USDT**")
        else:
            st.error("No se pudo obtener el precio. Revisa el par o tu conexión.")
            price_a = 0.0
    else:
        price_a = st.number_input("Precio de la cripto A en fiat", min_value=0.0, value=0.0)

    price_b = st.number_input("Precio de la cripto B en fiat (deja 1.0 para conversión directa a USD/Fiat)", min_value=0.0, value=1.0)

    if st.button("Calcular Conversión"):
        if price_a > 0 and price_b > 0:
            resultado = convert_crypto(amount, price_a, price_b)
            st.success(f"**Resultado:** {amount} equivale a **{resultado:.6f}** de la segunda moneda.")
        else:
            st.warning("Asegúrate de que los precios sean mayores a cero.")

# --- PESTAÑA 2: MARGEN P2P ---
with tab2:
    st.header("Margen y Arbitraje P2P")
    p2p_amount = st.number_input("Cantidad de cripto/USDT a operar", min_value=0.0, value=100.0, step=10.0)
    buy_price = st.number_input("Precio de COMPRA por unidad (Fiat)", min_value=0.0, value=36.50, step=0.1)
    sell_price = st.number_input("Precio de VENTA por unidad (Fiat)", min_value=0.0, value=37.20, step=0.1)

    rol = st.radio("Selecciona tu rol en Binance P2P para comisiones:", ["Taker (0% Comisión)", "Maker (0.28% Comisión)"])
    buy_fee_pct = 0.28 if "Maker" in rol else 0.0
    sell_fee_pct = 0.28 if "Maker" in rol else 0.0

    if st.button("Calcular Margen P2P"):
        res = calcular_p2p_profit(p2p_amount, buy_price, sell_price, buy_fee_pct, sell_fee_pct)

        # Mostrar resultados en métricas visuales atractivas
        col1, col2 = st.columns(2)
        col1.metric("Costo Total Compra", f"{res['total_cost']:.2f}")
        col2.metric("Ingreso Total Venta", f"{res['total_revenue']:.2f}")

        col3, col4 = st.columns(2)
        col3.metric("Margen Bruto", f"{res['p2p_margin_pct']:.2f}%")
        col4.metric("Precio de Equilibrio", f"{res['break_even_price']:.4f}")

        st.subheader("Rendimiento Neto")
        if res['profit'] > 0:
            st.success(f"📈 **Rentable:** Ganancia neta de **+{res['profit']:.2f}** ({res['profit_pct']:.2f}%)")
        elif res['profit'] < 0:
            st.error(f"📉 **Pérdida:** Margen negativo de **{res['profit']:.2f}** ({res['profit_pct']:.2f}%)")
        else:
            st.warning("Punto de equilibrio perfecto (0 ganancias, 0 pérdidas).")

# --- PESTAÑA 3: PORCENTAJE DE CAMBIO ---
with tab3:
    st.header("Porcentaje de Cambio")
    inicial = st.number_input("Valor Inicial", min_value=0.0, value=10.0)
    final = st.number_input("Valor Final", min_value=0.0, value=12.0)

    if st.button("Calcular Cambio"):
        if inicial > 0:
            pct = porcentaje_cambio(inicial, final)
            st.info(f"**Cambio porcentual:** {pct:.2f}%")
        else:
            st.error("El valor inicial debe ser mayor a cero.")

# -------------------------------------------------------------------
# ESPACIO PARA FUTUROS ANUNCIOS (Sección fija abajo)
# -------------------------------------------------------------------
st.divider()
st.caption("📢 **Espacio Publicitario**")
contenedor_anuncio = st.container()
with contenedor_anuncio:
    # Por ahora dejamos un texto estético, en el futuro aquí insertas el banner o link afiliado.
    st.info("💡 ¿Quieres anunciar tu servicio de intercambio aquí? Contáctanos.")