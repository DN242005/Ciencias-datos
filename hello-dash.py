from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="AutoScope | Explorador Autos 10k",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Cambiamos la ruta para apuntar a tu nuevo archivo de 10,000 registros
DATA_PATH = Path(__file__).parent / "autos_10000.csv"
REQUIRED_COLUMNS = {
    "Manufacturer", "Model", "Type", "Price", "MPG.city", "MPG.highway",
    "EngineSize",
}


@st.cache_data
def load_cars():
    """Carga el dataset de 10k y normaliza los campos numéricos del análisis."""
    if not DATA_PATH.exists():
        st.error(f"No se encontró `{DATA_PATH.name}` en la carpeta del proyecto.")
        st.stop()

    cars = pd.read_csv(DATA_PATH)
    cars.columns = cars.columns.str.strip()
    missing_columns = REQUIRED_COLUMNS.difference(cars.columns)
    if missing_columns:
        st.error("Faltan columnas requeridas: " + ", ".join(sorted(missing_columns)))
        st.stop()

    numeric_columns = [
        "Price", "MPG.city", "MPG.highway", "EngineSize"
    ]
    for column in numeric_columns:
        cars[column] = pd.to_numeric(cars[column], errors="coerce")
    return cars


def metric_value(value, decimals=0, suffix=""):
    if pd.isna(value):
        return "N/D"
    return f"{value:,.{decimals}f}{suffix}"


cars = load_cars()

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Space+Mono&display=swap');
    :root { --ink: #dce9f5; --muted: #8ba5b8; --cyan: #5de3ff; --lime: #c7f36b; --panel: #10202e; }
    .stApp { background: radial-gradient(circle at 78% 0%, #16384d 0, #08131e 42%, #050b12 100%); color: var(--ink); }
    [data-testid="stHeader"] { background: transparent; }
    h1, h2, h3, p, label, .stMetric { font-family: 'Space Grotesk', sans-serif; }
    h1 { letter-spacing: 0; font-size: clamp(2.4rem, 5vw, 4.8rem); line-height: .98; }
    h2, h3 { color: var(--cyan); letter-spacing: 0; }
    .hero { border-left: 3px solid var(--cyan); padding: .25rem 0 .25rem 1.2rem; margin: 1.4rem 0 2rem; }
    .eyebrow { color: var(--lime); font-family: 'Space Mono', monospace; font-size: .72rem; letter-spacing: .14em; }
    .hero-copy { color: var(--muted); max-width: 720px; font-size: 1.05rem; }
    [data-testid="stMetric"] { background: rgba(16, 32, 46, .82); border: 1px solid #21455b; border-radius: 8px; padding: 1rem; box-shadow: 0 0 22px rgba(93,227,255,.07); }
    [data-testid="stMetricLabel"] { color: var(--muted); }
    [data-testid="stMetricValue"] { color: var(--cyan); font-family: 'Space Mono', monospace; }
    section[data-testid="stSidebar"] { background: #08131e; border-right: 1px solid #21455b; }
    .section-label { color: var(--lime); font-family: 'Space Mono', monospace; font-size: .78rem; letter-spacing: .08em; margin: 1.8rem 0 .5rem; }
    div[data-testid="stDataFrame"] { border: 1px solid #21455b; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
      <div class="eyebrow">AUTOSCOPE / 10K RECORDS EXPLORER</div>
      <h1>Radar automotriz masivo</h1>
      <p class="hero-copy">Explora precios, rendimiento y especificaciones de 10,000 vehículos del catálogo.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("### Panel de control")
    st.caption("Ajusta los filtros para el catálogo masivo.")
    type_options = sorted(cars["Type"].dropna().astype(str).unique())
    selected_types = st.multiselect("Tipo de vehículo", type_options, default=type_options)
    
    price_min = float(cars["Price"].min())
    price_max = float(cars["Price"].max())
    selected_price = st.slider(
        "Rango de precio (miles USD)", price_min, price_max,
        (price_min, price_max), step=0.5,
    )

filtered_cars = cars[
    cars["Type"].astype(str).isin(selected_types)
    & cars["Price"].between(*selected_price)
].copy()

st.markdown('<div class="section-label">/ LIVE METRICS</div>', unsafe_allow_html=True)
metric_columns = st.columns(3)
with metric_columns[0]:
    st.metric("Vehículos seleccionados", f"{len(filtered_cars):,}")
with metric_columns[1]:
    st.metric("Precio promedio", metric_value(filtered_cars["Price"].mean(), 1, " kUSD"))
with metric_columns[2]:
    st.metric("MPG ciudad promedio", metric_value(filtered_cars["MPG.city"].mean(), 1))

plt.rcParams.update({"font.family": "DejaVu Sans", "axes.titleweight": "bold"})
chart_face = "#10202e"
text_color = "#dce9f5"
accent = "#5de3ff"
accent_alt = "#c7f36b"


def finish_chart(figure):
    figure.tight_layout()
    st.pyplot(figure, use_container_width=True)
    plt.close(figure)


st.markdown('<div class="section-label">/ VISUAL ANALYTICS</div>', unsafe_allow_html=True)
first_row = st.columns(2)
with first_row[0]:
    figure, axis = plt.subplots(figsize=(8, 4), facecolor=chart_face)
    axis.set_facecolor(chart_face)
    axis.hist(filtered_cars["Price"].dropna(), bins=20, color=accent, alpha=.84, edgecolor="#08131e")
    axis.set_title("Distribución de precios", color=text_color)
    axis.set_xlabel("Precio (miles USD)", color=text_color)
    axis.set_ylabel("Cantidad de vehículos", color=text_color)
    axis.tick_params(colors=text_color)
    finish_chart(figure)
with first_row[1]:
    type_counts = filtered_cars["Type"].value_counts().sort_values()
    figure, axis = plt.subplots(figsize=(8, 4), facecolor=chart_face)
    axis.set_facecolor(chart_face)
    axis.barh(type_counts.index, type_counts.values, color=accent_alt)
    axis.set_title("Vehículos por tipo", color=text_color)
    axis.set_xlabel("Cantidad de vehículos", color=text_color)
    axis.tick_params(colors=text_color)
    finish_chart(figure)

second_row = st.columns(2)
with second_row[0]:
    scatter_data = filtered_cars.dropna(subset=["EngineSize", "MPG.city"]).sample(min(1000, len(filtered_cars)))
    figure, axis = plt.subplots(figsize=(8, 4), facecolor=chart_face)
    axis.set_facecolor(chart_face)
    axis.scatter(scatter_data["EngineSize"], scatter_data["MPG.city"], alpha=.4, s=20, color=accent)
    axis.set_title("Tamaño de motor vs rendimiento urbano", color=text_color)
    axis.set_xlabel("Tamaño de motor (Litros)", color=text_color)
    axis.set_ylabel("MPG en ciudad", color=text_color)
    axis.tick_params(colors=text_color)
    finish_chart(figure)
with second_row[1]:
    top_cars = filtered_cars.nlargest(10, "Price").sort_values("Price")
    top_cars["Label"] = top_cars["Manufacturer"] + " " + top_cars["Model"]
    figure, axis = plt.subplots(figsize=(8, 4), facecolor=chart_face)
    axis.set_facecolor(chart_face)
    axis.barh(top_cars["Label"], top_cars["Price"], color=accent)
    axis.set_title("Top 10 vehículos más costosos", color=text_color)
    axis.set_xlabel("Precio (miles USD)", color=text_color)
    axis.tick_params(colors=text_color, labelsize=8)
    finish_chart(figure)

st.markdown('<div class="section-label">/ FILTERED CATALOG</div>', unsafe_allow_html=True)
st.subheader("Vehículos seleccionados")
st.write(f"{len(filtered_cars):,} registros después de aplicar los filtros")
table_columns = [
    "Manufacturer", "Model", "Type", "Price", "MPG.city", "MPG.highway",
    "EngineSize",
]
st.dataframe(
    filtered_cars[table_columns].sort_values("Price", ascending=False),
    use_container_width=True,
    hide_index=True,
)