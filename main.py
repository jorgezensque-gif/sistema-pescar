import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sqlite3
from datetime import datetime

# --- CONFIGURAÇÕES GERAIS ---
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

# --- FUNÇÕES DE BANCO ---
def get_connection():
    return sqlite3.connect('pescar_v5.db', check_same_thread=False)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS avaliacoes 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, etapa TEXT, 
                 j1 INT, j2 INT, j3 INT, j4 INT, j5 INT, j6 INT, j7 INT,
                 g1 INT, g2 INT, g3 INT, g4 INT, g5 INT, g6 INT, g7 INT,
                 status TEXT, data TEXT)''')
    conn.commit()
    conn.close()

init_db()
st.set_page_config(page_title="SAP Pescar 2026", layout="wide")

# --- MENU LATERAL ---
st.sidebar.title("📌 Sistema SAP")
modo = st.sidebar.radio("Navegar para:", ["Área do Aluno", "Painel do Gestor (Jorge)"])

# --- ÁREA DO ALUNO ---
if modo == "Área do Aluno":
    st.header("📝 Autoavaliação do Jovem")
    with st.form("form_jovem", clear_on_submit=True):
        nome = st.text_input("Nome Completo do Jovem:")
        etapa = st.selectbox("Selecione a Etapa:", ["Etapa 1", "Etapa 2"])
        
        notas_j = []
        for comp in COMPETENCIAS:
            st.subheader(comp)
            st.info(DESC_PESCAR[comp])
            # index=None obriga o aluno a clicar, não vem nada marcado.
            n = st.radio(f"Nota (1 a 5):", [1, 2, 3, 4, 5], index=None, horizontal=True, key=f"j_{comp}")
            notas_j.append(n)
            st.write("---")
            
        if st.form_submit_button("ENVIAR MINHA AVALIAÇÃO"):
            if nome and all(v is not None for v in notas_j):
                conn = get_connection()
                c = conn.cursor()
                c.execute("INSERT INTO avaliacoes (nome, etapa, j1,j2,j3,j4,j5,j6,j7, status, data) VALUES (?,?,?,?,?,?,?,?,?,?,?)", 
                          (nome, etapa, *notas_j, "Pendente", datetime.now().strftime("%d/%m/%Y")))
                conn.commit()
                conn.close()
                st.success(f"✅ Feito! Avise o Jorge que {nome} já enviou.")
            else:
                st.error("❌ Erro: Preencha seu nome e TODAS as notas de 1 a 5.")

# --- PAINEL DO GESTOR ---
elif modo == "Painel do Gestor (Jorge)":
    senha = st.sidebar.text_input("Senha:", type="password")
    if senha == "jorge2026":
        st.header("📊 Painel de Controle - Educador Jorge")
        
        conn = get_connection()
        df = pd.read_sql("SELECT * FROM avaliacoes", conn)
        conn.close()

        if df.empty:
            st.warning("📭 Nenhuma avaliação enviada pelos alunos ainda.")
        else:
            pendentes = df[df['status'] == "Pendente"]
            if not pendentes.empty:
                st.subheader("⭐ Alunos para você dar nota (Gestor)")
                id_aluno = st.selectbox("Selecione o aluno:", pendentes['id'].tolist(), 
                                       format_func=lambda x: df[df['id']==x]['nome'].values[0])
                
                with st.form("form_gestor"):
                    notas_g = []
                    for comp in COMPETENCIAS:
                        ng = st.radio(f"Sua nota para {comp}:", [1, 2, 3, 4, 5], index=None, horizontal=True)
                        notas_g.append(ng)
                    
                    if st.form_submit_button("SALVAR MINHA NOTA E FINALIZAR"):
                        if all(v is not None for v in notas_g):
                            conn = get_connection()
                            c = conn.cursor()
                            c.execute("UPDATE avaliacoes SET g1=?, g2=?, g3=?, g4=?, g5=?, g6=?, g7=?, status='Finalizado' WHERE id=?", (*notas_g, id_aluno))
                            conn.commit()
                            conn.close()
                            st.success("Avaliação finalizada!")
                            st.rerun()
                        else: st.error("Dê todas as notas de 1 a 5.")
            
            # --- GRÁFICOS ---
            finalizados = df[df['status'] == 'Finalizado']
            if not finalizados.empty:
                st.write("---")
                st.subheader("📈 Resultado Final (Média Jovem + Gestor)")
                aluno_v = st.selectbox("Ver Gráfico de:", finalizados['nome'].unique())
                d = finalizados[finalizados['nome'] == aluno_v].iloc[-1]
                
                # Média entre Jovem e Gestor
                medias = [(d[f'j{i}'] + d[f'g{i}'])/2 for i in range(1,8)]
                
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(r=medias, theta=COMPETENCIAS, fill='toself', name='Média'))
                fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), showlegend=False)
                st.plotly_chart(fig)
            else:
                st.info("Aguardando você finalizar a primeira avaliação para mostrar o gráfico.")
    elif senha != "":
        st.error("Senha incorreta.")
