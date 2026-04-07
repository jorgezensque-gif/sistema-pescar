import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sqlite3
from datetime import datetime

# --- CONFIGURAÇÕES E TEXTOS DO PDF ---
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
            # VOLTOU PARA BOTÃO DE 1 A 5 (SEM BARRA)
            n = st.radio(f"Sua nota (1-5):", [1, 2, 3, 4, 5], index=2, horizontal=True, key=f"j_{titulo}")
            notas_j.append(n)
            st.write("---")
            
        if st.form_submit_button("ENVIAR PARA O JORGE"):
            if nome:
                conn = sqlite3.connect('pescar_final.db')
                c = conn.cursor()
                c.execute("INSERT INTO avaliacoes (nome, etapa, j1,j2,j3,j4,j5,j6,j7, status, data) VALUES (?,?,?,?,?,?,?,?,?,?,?)", 
                          (nome, etapa, *notas_j, "Aguardando Jorge", datetime.now().strftime("%d/%m/%Y")))
                conn.commit()
                conn.close()
                st.success("✅ Enviado com sucesso! Avise o Jorge.")
            else: st.error("Por favor, preencha o seu nome!")

elif modo == "Painel do Gestor (Jorge)":
    senha = st.sidebar.text_input("Senha de Acesso:", type="password")
    if senha == "jorge2026":
        st.header("📊 Painel de Avaliação do Educador")
        conn = sqlite3.connect('pescar_final.db')
        df = pd.read_sql("SELECT * FROM avaliacoes", conn)
        conn.close()

        if not df.empty:
            pendentes = df[df['status'] == "Aguardando Jorge"]
            if not pendentes.empty:
                st.subheader("⭐ Dar nota do Gestor (1 a 5)")
                id_aluno = st.selectbox("Escolha o aluno para avaliar:", pendentes['id'].tolist(), 
                                       format_func=lambda x: df[df['id']==x]['nome'].values[0])
                
                with st.form("form_gestor"):
                    notas_g = []
                    for titulo in INFOS_PESCAR.keys():
                        # GESTOR TAMBÉM USA BOTÃO DE 1 A 5
                        ng = st.radio(f"Sua nota para {titulo}:", [1, 2, 3, 4, 5], index=2, horizontal=True)
                        notas_g.append(ng)
                    
                    if st.form_submit_button("FINALIZAR E GERAR GRÁFICO"):
                        conn = sqlite3.connect('pescar_final.db')
                        c = conn.cursor()
                        c.execute("UPDATE avaliacoes SET g1=?, g2=?, g3=?, g4=?, g5=?, g6=?, g7=?, status='Finalizado' WHERE id=?", (*notas_g, id_aluno))
                        conn.commit()
                        conn.close()
                        st.rerun()

            st.write("---")
            st.subheader("📈 Resultado Final (Média Jovem + Gestor)")
            finalizados = df[df['status'] == 'Finalizado']
            if not finalizados.empty:
                aluno_v = st.selectbox("Ver Gráfico de:", finalizados['nome'].unique())
                d = finalizados[finalizados['nome'] == aluno_v].iloc[-1]
                
                # Média entre a nota do Jovem e do Gestor
                medias = [(d[f'j{i}'] + d[f'g{i}'])/2 for i in range(1,8)]
                
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(r=medias, theta=list(INFOS_PESCAR.keys()), fill='toself', name='Resultado Final'))
                fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), title=f"Desempenho: {aluno_v}")
                st.plotly_chart(fig)
        else:
            st.warning("O painel está vazio. Peça para um aluno preencher primeiro!")
