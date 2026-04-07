import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sqlite3
from datetime import datetime

# --- CONFIGURAÇÃO ---
COMPETENCIAS = [
    "1-SER PROTAGONISTA", "2-SER RESPONSÁVEL E COMPROMETIDO", 
    "3-COMPREENDER CONTEXTOS E COMUNICAR-SE", "4-SER DEMOCRÁTICO, ÉTICO E CIDADÃO", 
    "5-RESOLVER SITUAÇÕES PROBLEMA", "6-TRABALHAR E PRODUZIR EM EQUIPE", 
    "7-APRENDER A APRENDER"
]

# --- BANCO DE DADOS (VERSÃO FINAL SEM TRAVAMENTO) ---
def init_db():
    conn = sqlite3.connect('pescar_v9_destravado.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS avaliacoes 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, etapa TEXT, 
                 j1 INT, j2 INT, j3 INT, j4 INT, j5 INT, j6 INT, j7 INT,
                 g1 INT, g2 INT, g3 INT, g4 INT, g5 INT, g6 INT, g7 INT,
                 status TEXT, data TEXT)''')
    conn.commit()
    conn.close()

init_db()
st.set_page_config(page_title="Sistema SAP Pescar", layout="wide")

st.sidebar.title("📌 Menu Principal")
modo = st.sidebar.radio("Selecione:", ["Área do Aluno (Responder)", "Painel do Gestor (Jorge)"])

# --- 1. ÁREA DO ALUNO ---
if modo == "Área do Aluno (Responder)":
    st.header("📝 Autoavaliação do Jovem")
    st.info("Notas de 1 a 5. Selecione todas as opções antes de enviar.")
    
    with st.form("form_aluno"):
        nome = st.text_input("Seu Nome Completo:")
        etapa = st.selectbox("Qual Etapa?", ["Etapa 1", "Etapa 2"])
        
        notas_j = []
        for comp in COMPETENCIAS:
            st.write(f"**{comp}**")
            # index=None garante que venha EM BRANCO
            n = st.radio(f"Sua nota:", [1, 2, 3, 4, 5], index=None, horizontal=True, key=f"al_{comp}")
            notas_j.append(n)
            st.write("---")
            
        if st.form_submit_button("ENVIAR AVALIAÇÃO"):
            if nome and all(v is not None for v in notas_j):
                conn = sqlite3.connect('pescar_v9_destravado.db')
                c = conn.cursor()
                c.execute("INSERT INTO avaliacoes (nome, etapa, j1,j2,j3,j4,j5,j6,j7, status, data) VALUES (?,?,?,?,?,?,?,?,?,?,?)", 
                          (nome, etapa, *notas_j, "PENDENTE", datetime.now().strftime("%d/%m/%Y")))
                conn.commit()
                conn.close()
                st.success("✅ Enviado! Agora o Jorge fará a avaliação dele.")
            else:
                st.error("❌ Por favor, preencha seu nome e todas as notas.")

# --- 2. PAINEL DO GESTOR (CORRIGIDO) ---
elif modo == "Painel do Gestor (Jorge)":
    # A senha só é validada se você escrever algo. Se estiver vazio, ele não dá erro de "Senha Incorreta".
    senha_digitada = st.sidebar.text_input("Senha de Acesso:", type="password")
    
    if senha_digitada == "":
        st.info("Digite a senha no menu lateral para acessar os dados.")
    
    elif senha_digitada == "jorge2026":
        st.header("📊 Painel do Educador")
        
        conn = sqlite3.connect('pescar_v9_destravado.db')
        df = pd.read_sql("SELECT * FROM avaliacoes", conn)
        conn.close()

        if df.empty:
            st.warning("Aguardando as primeiras respostas dos jovens.")
        else:
            # PARTE DE AVALIAR PENDENTES
            pendentes = df[df['status'] == "PENDENTE"]
            if not pendentes.empty:
                st.subheader("⭐ Avaliações Pendentes")
                aluno_id = st.selectbox("Escolha o aluno:", pendentes['id'].tolist(), 
                                       format_func=lambda x: df[df['id']==x]['nome'].values[0])
                
                with st.form("form_gestor"):
                    notas_g = []
                    for comp in COMPETENCIAS:
                        ng = st.radio(f"Nota para {comp}:", [1, 2, 3, 4, 5], index=None, horizontal=True)
                        notas_g.append(ng)
                    
                    if st.form_submit_button("FINALIZAR"):
                        if all(v is not None for v in notas_g):
                            conn = sqlite3.connect('pescar_v9_destravado.db')
                            c = conn.cursor()
                            c.execute("UPDATE avaliacoes SET g1=?, g2=?, g3=?, g4=?, g5=?, g6=?, g7=?, status='F' WHERE id=?", (*notas_g, aluno_id))
                            conn.commit()
                            conn.close()
                            st.success("Avaliação finalizada!")
                            st.rerun()
                        else:
                            st.error("Preencha todas as notas de 1 a 5.")

            # PARTE DE VER GRÁFICOS
            finalizados = df[df['status'] == 'F']
            if not finalizados.empty:
                st.write("---")
                st.subheader("📈 Resultado Final")
                aluno_v = st.selectbox("Ver resultado de:", finalizados['nome'].unique())
                d = finalizados[finalizados['nome'] == aluno_v].iloc[-1]
                
                # Cálculo da média
                medias = [(float(d[f'j{i}']) + float(d[f'g{i}']))/2 for i in range(1,8)]
                
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(r=medias, theta=COMPETENCIAS, fill='toself'))
                fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])))
                st.plotly_chart(fig)
            else:
                st.info("Assim que você avaliar um aluno, o gráfico aparecerá aqui.")
    
    else:
        st.error("❌ Senha incorreta. Tente novamente.")
