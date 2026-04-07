import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sqlite3
from datetime import datetime

# --- CONFIGURAÇÃO DE TEXTOS ---
COMPETENCIAS = [
    "1-SER PROTAGONISTA", "2-SER RESPONSÁVEL E COMPROMETIDO", 
    "3-COMPREENDER CONTEXTOS E COMUNICAR-SE", "4-SER DEMOCRÁTICO, ÉTICO E CIDADÃO", 
    "5-RESOLVER SITUAÇÕES PROBLEMA", "6-TRABALHAR E PRODUZIR EM EQUIPE", 
    "7-APRENDER A APRENDER"
]

DESC_PESCAR = {
    "1-SER PROTAGONISTA": "Jovem que se conscientiza de sua identidade, atua com autonomia e constrói seu destino.",
    "2-SER RESPONSÁVEL E COMPROMETIDO": "Comprometimento, pontualidade, assiduidade e respeito a regras.",
    "3-COMPREENDER CONTEXTOS E COMUNICAR-SE": "Capacidade de compreender o outro e expressar-se com clareza.",
    "4-SER DEMOCRÁTICO, ÉTICO E CIDADÃO": "Integridade, respeito à diversidade e participação comunitária.",
    "5-RESOLVER SITUAÇÕES PROBLEMA": "Identificar problemas e propor soluções criativas.",
    "6-TRABALHAR E PRODUZIR EM EQUIPE": "Colaborar e partilhar, colocando o grupo acima do pessoal.",
    "7-APRENDER A APRENDER": "Habilidade para buscar e construir novos conhecimentos."
}

# --- BANCO DE DADOS (USANDO TRY PARA NÃO TRAVAR) ---
def init_db():
    try:
        conn = sqlite3.connect('pescar_vFinal.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS avaliacoes 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, etapa TEXT, 
                     j1 INT, j2 INT, j3 INT, j4 INT, j5 INT, j6 INT, j7 INT,
                     g1 INT, g2 INT, g3 INT, g4 INT, g5 INT, g6 INT, g7 INT,
                     status TEXT, data TEXT)''')
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Erro ao iniciar banco: {e}")

init_db()
st.set_page_config(page_title="SAP Pescar", layout="wide")

st.sidebar.title("📌 Menu")
modo = st.sidebar.radio("Ir para:", ["Área do Aluno", "Painel do Gestor"])

# --- 1. ÁREA DO ALUNO ---
if modo == "Área do Aluno":
    st.header("📝 Avaliação do Jovem")
    with st.form("form_jovem"):
        nome = st.text_input("Seu Nome Completo:")
        etapa = st.selectbox("Etapa:", ["Etapa 1", "Etapa 2"])
        
        respostas_j = []
        for comp in COMPETENCIAS:
            st.write(f"**{comp}**")
            st.caption(DESC_PESCAR[comp])
            # index=None deixa EM BRANCO para não influenciar
            v = st.radio("Sua nota:", [1, 2, 3, 4, 5], index=None, horizontal=True, key=f"aluno_{comp}")
            respostas_j.append(v)
            st.write("---")
            
        if st.form_submit_button("ENVIAR AVALIAÇÃO"):
            if nome and all(n is not None for n in respostas_j):
                conn = sqlite3.connect('pescar_vFinal.db')
                c = conn.cursor()
                c.execute("INSERT INTO avaliacoes (nome, etapa, j1,j2,j3,j4,j5,j6,j7, status, data) VALUES (?,?,?,?,?,?,?,?,?,?,?)", 
                          (nome, etapa, *respostas_j, "Pendente", datetime.now().strftime("%d/%m/%Y")))
                conn.commit()
                conn.close()
                st.success("✅ Enviado com sucesso!")
            else:
                st.error("❌ Por favor, preencha o nome e selecione todas as notas.")

# --- 2. PAINEL DO GESTOR ---
elif modo == "Painel do Gestor":
    senha = st.sidebar.text_input("Senha:", type="password")
    if senha == "jorge2026":
        st.header("📊 Painel do Educador Jorge")
        
        try:
            conn = sqlite3.connect('pescar_vFinal.db')
            df = pd.read_sql("SELECT * FROM avaliacoes", conn)
            conn.close()
        except:
            df = pd.DataFrame()

        if df.empty:
            st.info("Ainda não há avaliações para mostrar.")
        else:
            # Filtrar quem precisa de nota do Jorge
            pendentes = df[df['status'] == "Pendente"]
            if not pendentes.empty:
                st.subheader("⭐ Avaliações para Finalizar")
                aluno_id = st.selectbox("Escolha o aluno:", pendentes['id'].tolist(), 
                                       format_func=lambda x: df[df['id']==x]['nome'].values[0])
                
                with st.form("form_gestor"):
                    respostas_g = []
                    for comp in COMPETENCIAS:
                        vg = st.radio(f"Sua nota para {comp}:", [1, 2, 3, 4, 5], index=None, horizontal=True)
                        respostas_g.append(vg)
                    
                    if st.form_submit_button("SALVAR NOTAS"):
                        if all(n is not None for n in respostas_g):
                            conn = sqlite3.connect('pescar_vFinal.db')
                            c = conn.cursor()
                            c.execute("UPDATE avaliacoes SET g1=?, g2=?, g3=?, g4=?, g5=?, g6=?, g7=?, status='F' WHERE id=?", (*respostas_g, aluno_id))
                            conn.commit()
                            conn.close()
                            st.success("Finalizado!")
                            st.rerun()
                        else: st.error("Marque todas as notas.")
            
            # Gráficos (Só aparece se houver avaliações finalizadas 'F')
            finalizados = df[df['status'] == 'F']
            if not finalizados.empty:
                st.write("---")
                aluno_v = st.selectbox("Ver Gráfico de:", finalizados['nome'].unique())
                d = finalizados[finalizados['nome'] == aluno_v].iloc[-1]
                medias = [(d[f'j{i}'] + d[f'g{i}'])/2 for i in range(1,8)]
                
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(r=medias, theta=COMPETENCIAS, fill='toself'))
                fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])))
                st.plotly_chart(fig)
            else:
                st.write("Aguardando você avaliar o primeiro aluno.")

    elif senha != "":
        st.error("Senha incorreta.")
