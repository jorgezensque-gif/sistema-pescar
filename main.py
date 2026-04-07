import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sqlite3
from datetime import datetime
import io

# --- CONFIGURAÇÃO ---
COMPETENCIAS = [
    "1-SER PROTAGONISTA", "2-SER RESPONSÁVEL E COMPROMETIDO", 
    "3-COMPREENDER CONTEXTOS E COMUNICAR-SE", "4-SER DEMOCRÁTICO, ÉTICO E CIDADÃO", 
    "5-RESOLVER SITUAÇÕES PROBLEMA", "6-TRABALHAR E PRODUZIR EM EQUIPE", 
    "7-APRENDER A APRENDER"
]

def init_db():
    conn = sqlite3.connect('pescar_v13.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS avaliacoes 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, etapa TEXT, 
                 j1 INT, j2 INT, j3 INT, j4 INT, j5 INT, j6 INT, j7 INT,
                 g1 INT, g2 INT, g3 INT, g4 INT, g5 INT, g6 INT, g7 INT,
                 status TEXT, data TEXT)''')
    conn.commit()
    conn.close()

init_db()
st.set_page_config(page_title="SAP Pescar - Palmas", layout="wide")

st.sidebar.title("📌 Menu")
modo = st.sidebar.radio("Navegar:", ["Aluno (Responder)", "Gestor (Jorge)"])

# --- 1. ÁREA DO ALUNO ---
if modo == "Aluno (Responder)":
    st.header("📝 Avaliação do Jovem")
    with st.form("form_aluno"):
        nome = st.text_input("Nome do Jovem:")
        etapa = st.selectbox("Etapa:", ["Etapa 1", "Etapa 2"])
        notas = []
        for c in COMPETENCIAS:
            st.write(f"**{c}**")
            n = st.radio("Nota (1-5):", [1, 2, 3, 4, 5], index=None, horizontal=True, key=f"al_{c}")
            notas.append(n)
        if st.form_submit_button("ENVIAR"):
            if nome and all(v is not None for v in notas):
                conn = sqlite3.connect('pescar_v13.db')
                c = conn.cursor()
                c.execute("INSERT INTO avaliacoes (nome, etapa, j1,j2,j3,j4,j5,j6,j7, status, data) VALUES (?,?,?,?,?,?,?,?,?,?,?)", 
                          (nome, etapa, *notas, "Pendente", datetime.now().strftime("%d/%m/%Y")))
                conn.commit()
                conn.close()
                st.success("✅ Enviado com sucesso!")
            else: st.error("Preencha todos os campos.")

# --- 2. PAINEL DO GESTOR ---
elif modo == "Gestor (Jorge)":
    senha = st.sidebar.text_input("Senha:", type="password")
    if senha == "jorge2026":
        tab1, tab2, tab3, tab4 = st.tabs(["⭐ Avaliar", "👤 Individual", "👥 Turma Toda", "📥 Dados"])
        
        conn = sqlite3.connect('pescar_v13.db')
        df = pd.read_sql("SELECT * FROM avaliacoes", conn)
        conn.close()

        # ABA 1: LANÇAR NOTAS DO JORGE
        with tab1:
            pendentes = df[df['status'] == "Pendente"]
            if not pendentes.empty:
                id_al = st.selectbox("Aluno:", pendentes['id'].tolist(), format_func=lambda x: df[df['id']==x]['nome'].values[0])
                with st.form("f_jorge"):
                    notas_g = [st.radio(c, [1, 2, 3, 4, 5], index=None, horizontal=True) for c in COMPETENCIAS]
                    if st.form_submit_button("SALVAR MINHA AVALIAÇÃO"):
                        conn = sqlite3.connect('pescar_v13.db')
                        conn.execute(f"UPDATE avaliacoes SET g1=?,g2=?,g3=?,g4=?,g5=?,g6=?,g7=?, status='F' WHERE id={id_al}", (*notas_g,))
                        conn.commit()
                        st.rerun()
            else: st.info("Nenhum pendente.")

        # ABA 2: GRÁFICOS INDIVIDUAIS (RADAR E BARRA)
        with tab2:
            finalizados = df[df['status'] == 'F']
            if not finalizados.empty:
                aluno = st.selectbox("Escolha o Aluno:", finalizados['nome'].unique())
                d = finalizados[finalizados['nome'] == aluno].iloc[-1]
                m_ind = [(float(d[f'j{i}'])+float(d[f'g{i}']))/2 for i in range(1,8)]
                
                col1, col2 = st.columns(2)
                with col1:
                    fig_ri = go.Figure(data=go.Scatterpolar(r=m_ind, theta=COMPETENCIAS, fill='toself'))
                    fig_ri.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), title="Radar Individual")
                    st.plotly_chart(fig_ri, use_container_width=True)
                with col2:
                    fig_bi = px.bar(x=COMPETENCIAS, y=m_ind, title="Barras Individual", color=m_ind, range_y=[0,5])
                    st.plotly_chart(fig_bi, use_container_width=True)

        # ABA 3: GRÁFICOS DA TURMA (RADAR E BARRA)
        with tab3:
            if not finalizados.empty:
                et = st.radio("Ver Turma na:", ["Etapa 1", "Etapa 2"], horizontal=True)
                df_et = finalizados[finalizados['etapa'] == et]
                if not df_et.empty:
                    m_turma = [round((df_et[f'j{i}'].mean() + df_et[f'g{i}'].mean())/2, 2) for i in range(1,8)]
                    col1, col2 = st.columns(2)
                    with col1:
                        fig_rt = go.Figure(data=go.Scatterpolar(r=m_turma, theta=COMPETENCIAS, fill='toself', line_color='green'))
                        fig_rt.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), title=f"Radar Geral - {et}")
                        st.plotly_chart(fig_rt, use_container_width=True)
                    with col2:
                        fig_bt = px.bar(x=COMPETENCIAS, y=m_turma, title=f"Barras Geral - {et}", color=m_turma, range_y=[0,5])
                        st.plotly_chart(fig_bt, use_container_width=True)

        # ABA 4: EXPORTAR E DELETAR
        with tab4:
            if not df.empty:
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False)
                st.download_button("📥 BAIXAR EXCEL", output.getvalue(), "projeto_pescar.xlsx")
                
                if st.button("🔴 LIMPAR TUDO (Cuidado!)"):
                    conn = sqlite3.connect('pescar_v13.db')
                    conn.execute("DELETE FROM avaliacoes")
                    conn.commit()
                    st.rerun()
