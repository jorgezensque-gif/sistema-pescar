import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sqlite3
from datetime import datetime

# --- TEXTOS DAS COMPETÊNCIAS ---
INFOS_PESCAR = {
    "1-SER PROTAGONISTA": "Protagonista é o jovem que se conscientiza de sua identidade, se reconhece como ser atuante, autônomo, solidário e construtor do seu destino.",
    "2-SER RESPONSÁVEL E COMPROMETIDO": "Comprometer-se com suas atividades, ser pontual e assíduo, cumprir o que é exigido e respeitar regras.",
    "3-COMPREENDER CONTEXTOS E COMUNICAR-SE": "Capacidade de compreender o outro e expressar-se de forma clara, objetiva e coerente.",
    "4-SER DEMOCRÁTICO, ÉTICO E CIDADÃO": "Agir com integridade, respeitar a diversidade e participar ativamente da vida comunitária.",
    "5-RESOLVER SITUAÇÕES PROBLEMA": "Identificar problemas, analisar situações e propor soluções criativas e eficazes.",
    "6-TRABALHAR E PRODUZIR EM EQUIPE": "Capacidade de colaborar e partilhar, colocando os interesses do grupo acima dos pessoais.",
    "7-APRENDER A APRENDER": "Habilidade para buscar, compreender e construir novos conhecimentos ao longo da vida."
}

def init_db():
    conn = sqlite3.connect('pescar_final.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS avaliacoes 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, etapa TEXT, 
                 j1 INT, j2 INT, j3 INT, j4 INT, j5 INT, j6 INT, j7 INT,
                 g1 INT, g2 INT, g3 INT, g4 INT, g5 INT, g6 INT, g7 INT,
                 status TEXT, data TEXT)''')
    conn.commit()
    conn.close()

init_db()
st.set_page_config(page_title="Sistema Pescar 2026", layout="wide")

st.sidebar.title("📌 Menu")
modo = st.sidebar.radio("Navegar:", ["Área do Aluno", "Painel do Gestor (Jorge)"])

if modo == "Área do Aluno":
    st.header("📝 Autoavaliação do Jovem")
    with st.form("form_jovem"):
        nome = st.text_input("Nome Completo do Jovem:")
        etapa = st.selectbox("Selecione a Etapa:", ["Etapa 1", "Etapa 2"])
        
        notas_j = []
        for titulo, desc in INFOS_PESCAR.items():
            st.markdown(f"### {titulo}")
            st.info(desc)
            # REGRA: index=None deixa as notas em BRANCO (obrigatório escolher)
            n = st.radio(f"Sua nota (1-5):", [1, 2, 3, 4, 5], index=None, horizontal=True, key=f"j_{titulo}")
            notas_j.append(n)
            st.write("---")
            
        if st.form_submit_button("ENVIAR AVALIAÇÃO"):
            if nome and all(v is not None for v in notas_j):
                conn = sqlite3.connect('pescar_final.db')
                c = conn.cursor()
                c.execute("INSERT INTO avaliacoes (nome, etapa, j1,j2,j3,j4,j5,j6,j7, status, data) VALUES (?,?,?,?,?,?,?,?,?,?,?)", 
                          (nome, etapa, *notas_j, "Aguardando Jorge", datetime.now().strftime("%d/%m/%Y")))
                conn.commit()
                conn.close()
                st.success("✅ Enviado! Suas respostas foram salvas em branco como solicitado.")
            else: st.error("Por favor, preencha o nome e selecione TODAS as notas.")

elif modo == "Painel do Gestor (Jorge)":
    senha = st.sidebar.text_input("Senha de Acesso:", type="password")
    if senha == "jorge2026":
        st.header("📊 Painel do Educador")
        conn = sqlite3.connect('pescar_final.db')
        df = pd.read_sql("SELECT * FROM avaliacoes", conn)
        conn.close()

        if not df.empty:
            pendentes = df[df['status'] == "Aguardando Jorge"]
            if not pendentes.empty:
                st.subheader("⭐ Avaliações Pendentes")
                id_aluno = st.selectbox("Escolha o aluno:", pendentes['id'].tolist(), 
                                       format_func=lambda x: df[df['id']==x]['nome'].values[0])
                
                with st.form("form_gestor"):
                    notas_g = []
                    for titulo in INFOS_PESCAR.keys():
                        ng = st.radio(f"Nota do Gestor para {titulo}:", [1, 2, 3, 4, 5], index=None, horizontal=True)
                        notas_g.append(ng)
                    
                    if st.form_submit_button("FINALIZAR"):
                        if all(v is not None for v in notas_g):
                            conn = sqlite3.connect('pescar_final.db')
                            c = conn.cursor()
                            c.execute("UPDATE avaliacoes SET g1=?, g2=?, g3=?, g4=?, g5=?, g6=?, g7=?, status='Finalizado' WHERE id=?", (*notas_g, id_aluno))
                            conn.commit()
                            conn.close()
                            st.rerun()
                        else: st.error("Dê todas as notas antes de finalizar.")
            
            # --- RESULTADOS ---
            finalizados = df[df['status'] == 'Finalizado']
            if not finalizados.empty:
                st.write("---")
                aluno_v = st.selectbox("Ver Gráfico de:", finalizados['nome'].unique())
                d = finalizados[finalizados['nome'] == aluno_v].iloc[-1]
                medias = [(d[f'j{i}'] + d[f'g{i}'])/2 for i in range(1,8)]
                
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(r=medias, theta=list(INFOS_PESCAR.keys()), fill='toself'))
                fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])))
                st.plotly_chart(fig)
        else:
            st.info("Nenhum dado encontrado no banco de dados.")
    else:
        st.error("Acesso restrito.")
