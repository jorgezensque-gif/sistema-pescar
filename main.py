import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
from datetime import datetime

# --- CONFIGURAÇÃO DAS COMPETÊNCIAS (PADRÃO PESCAR 2025) ---
COMPETENCIAS = [
    "Ser Protagonista", "Responsável e Comprometido", "Comunicação",
    "Ético e Cidadão", "Situações Problema", "Trabalho em Equipe", "Aprender a Aprender"
]

# --- FUNÇÕES DE BANCO DE DADOS (SQLite) ---
def init_db():
    conn = sqlite3.connect('pescar_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS avaliacoes 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, etapa TEXT, 
                 c1 REAL, c2 REAL, c3 REAL, c4 REAL, c5 REAL, c6 REAL, c7 REAL, data TEXT)''')
    conn.commit()
    conn.close()

def salvar_avaliacao(nome, etapa, notas):
    conn = sqlite3.connect('pescar_data.db')
    c = conn.cursor()
    data_hoje = datetime.now().strftime("%d/%m/%Y %H:%M")
    c.execute("INSERT INTO avaliacoes (nome, etapa, c1, c2, c3, c4, c5, c6, c7, data) VALUES (?,?,?,?,?,?,?,?,?,?)",
              (nome, etapa, *notas, data_hoje))
    conn.commit()
    conn.close()

# --- INTERFACE ---
init_db()
st.set_page_config(page_title="SAP Pescar 2025", layout="wide")

st.sidebar.title("🔐 Acesso")
modo = st.sidebar.radio("Ir para:", ["Área do Aluno (Avaliação)", "Painel do Gestor"])

if modo == "Área do Aluno (Avaliação)":
    st.header("📝 Avaliação de Competências Socioemocionais")
    st.info("Olá! Preencha sua avaliação abaixo. Suas respostas são enviadas diretamente para o educador.")
    
    with st.form("form_aluno"):
        nome_aluno = st.text_input("Seu Nome Completo:")
        etapa_aluno = st.selectbox("Qual etapa está realizando?", ["Etapa 1 (E1)", "Etapa 2 (E2)"])
        
        notas_input = []
        for comp in COMPETENCIAS:
            nota = st.select_slider(f"Nível de: {comp}", options=list(range(11)), value=5)
            notas_input.append(nota)
        
        if st.form_submit_button("Enviar Avaliação"):
            if nome_aluno:
                salvar_avaliacao(nome_aluno, etapa_aluno, notas_input)
                st.success(f"✅ Parabéns, {nome_aluno}! Sua avaliação foi salva.")
            else:
                st.error("Por favor, digite seu nome antes de enviar.")

elif modo == "Painel do Gestor":
    # SENHA PARA O JORGE ACESSAR
    senha = st.sidebar.text_input("Senha de Gestor:", type="password")
    if senha == "jorge2026": 
        st.header("📊 Painel de Monitoramento - Educador Jorge")
        
        conn = sqlite3.connect('pescar_data.db')
        df = pd.read_sql("SELECT * FROM avaliacoes", conn)
        conn.close()

        if not df.empty:
            tab1, tab2 = st.tabs(["📊 Visão Geral (Barras)", "🕸️ Evolução Individual (Radar)"])
            
            with tab1:
                st.subheader("Média da Turma (Visualização Geral)")
                medias = df[['c1','c2','c3','c4','c5','c6','c7']].mean()
                df_barras = pd.DataFrame({"Competência": COMPETENCIAS, "Média": medias.values})
                fig_barras = px.bar(df_barras, x="Competência", y="Média", color="Média", 
                                    range_y=[0,10], color_continuous_scale='RdYlGn', text_auto='.1f')
                st.plotly_chart(fig_barras, use_container_width=True)

            with tab2:
                aluno_sel = st.selectbox("Escolha o Aluno para ver a Evolução:", df['nome'].unique())
                df_aluno = df[df['nome'] == aluno_sel]
                
                fig_radar = go.Figure()
                for i, row in df_aluno.iterrows():
                    fig_radar.add_trace(go.Scatterpolar(
                        r=[row['c1'], row['c2'], row['c3'], row['c4'], row['c5'], row['c6'], row['c7']],
                        theta=COMPETENCIAS, fill='toself', name=row['etapa']
                    ))
                fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 10])), title=f"Evolução de {aluno_sel}")
                st.plotly_chart(fig_radar)
        else:
            st.warning("Ainda não existem avaliações no banco de dados.")
    else:
        st.error("Acesso restrito ao Gestor.")