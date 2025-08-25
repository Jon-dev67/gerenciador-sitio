import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from io import BytesIO

# ================================
# CONFIGURAÇÕES INICIAIS
# ================================
st.set_page_config(
    page_title="🌱 Gerenciador de Produção",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilo do gráfico
plt.style.use("seaborn-v0_8-darkgrid")

# Locais de produção
estufas = [f"Estufa {i}" for i in range(1, 7)]
campos = [f"Campo {i}" for i in range(1, 14)]
locais = estufas + campos

# Produtos disponíveis
produtos = [
    "Tomate",
    "Abóbora Itália",
    "Abóbora Menina",
    "Pepino Japonês",
    "Pepino Caipira"
]

# Arquivo de dados
ARQUIVO_DADOS = "colheitas.xlsx"

# ================================
# CARREGAR OU CRIAR DADOS
# ================================
def carregar_dados():
    try:
        df = pd.read_excel(ARQUIVO_DADOS)
        if "Data" in df.columns:
            df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=["Data", "Local", "Produto", "Caixas"])

df = carregar_dados()

# ================================
# INTERFACE
# ================================
st.title("🌱 Gerenciador de Produção")
st.markdown("### Cadastro de Produção por Local")

col1, col2, col3 = st.columns(3)

with col1:
    local = st.selectbox("📍 Escolha o Local", locais)

with col2:
    produto = st.selectbox("🥒 Produto", produtos)

with col3:
    caixas = st.number_input("📦 Caixas Colhidas", min_value=0, step=1)

if st.button("➕ Adicionar Produção"):
    novo_registro = pd.DataFrame([{
        "Data": datetime.now(),
        "Local": local,
        "Produto": produto,
        "Caixas": caixas
    }])
    df = pd.concat([df, novo_registro], ignore_index=True)
    df.to_excel(ARQUIVO_DADOS, index=False)
    st.success("✅ Produção registrada com sucesso!")

# ================================
# VISUALIZAÇÃO
# ================================
st.markdown("---")
st.subheader("📊 Distribuição da Produção por Local")

if not df.empty:
    resumo = df.groupby("Local")["Caixas"].sum()

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(resumo, labels=resumo.index, autopct="%1.1f%%", startangle=90)
    ax.set_title("Proporção da Produção por Local")

    st.pyplot(fig)

    st.markdown("### 📋 Dados Registrados")

    # Resetar index para poder mostrar e selecionar
    df_reset = df.reset_index(drop=True)

    # Mostrar tabela com índice
    st.dataframe(df_reset)

    # Seleção de registro para excluir
    idx_excluir = st.number_input(
        "Digite o número da linha que deseja excluir:",
        min_value=0,
        max_value=len(df_reset) - 1,
        step=1
    )

    if st.button("🗑️ Excluir registro selecionado"):
        df = df.drop(df_reset.index[idx_excluir]).reset_index(drop=True)
        df.to_excel(ARQUIVO_DADOS, index=False)
        st.success(f"✅ Registro da linha {idx_excluir} excluído com sucesso!")
        st.rerun()
  # recarrega a página para atualizar

    # ================================
    # BOTÃO DE DOWNLOAD
    # ================================
    from io import BytesIO
    buffer = BytesIO()
    df.to_excel(buffer, index=False, engine="openpyxl")
    buffer.seek(0)

    st.download_button(
        label="📥 Baixar dados em Excel",
        data=buffer,
        file_name="colheitas.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

else:
    st.info("Nenhum dado registrado ainda. Adicione sua primeira produção acima 👆")
