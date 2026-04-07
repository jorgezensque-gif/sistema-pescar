import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
from datetime import datetime

# --- DICIONÁRIO DE PERGUNTAS (EXTRAÍDO DO SEU PDF) ---
INFOS_PESCAR = {
    "1-SER PROTAGONISTA": "Protagonista é o jovem que se conscientiza de sua identidade, se reconhece como ser atuante, autônomo, solidário e construtor do seu destino.",
    "2-SER RESPONSÁVEL E COMPROMETIDO": "Comprometer-se com suas atividades, ser pontual e assíduo, cumprir o que é exigido e respeitar regras.",
    "3-COMPREENDER CONTEXTOS E COMUNICAR-SE": "Capacidade de compreender o outro e expressar-se de forma clara, objetiva e coerente.",
    "4-SER DEMOCRÁTICO, ÉTICO E CIDADÃO": "Agir com integridade, respeitar a diversidade e participar ativamente da vida comunitária.",
    "5-RESOLVER SITUAÇÕES PROBLEMA": "Identificar problemas, analisar situações e propor soluções criativas e eficazes.",
    "6-TRABALHAR E PRODUZIR EM EQUIPE": "Capacidade de colaborar e partilhar, colocando os interesses do grupo acima dos pessoais.",
    "7-APRENDER A APRENDER": "Habilidade para buscar, compreender e construir novos conhecimentos ao longo da vida."
}

# --- BANCO DE DADOS ---
def init_db():
    conn = sqlite3.connect('pescar_v3.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS avaliacoes 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, etapa TEXT, 
                 c1_jovem INT, c2_jovem INT, c3_jovem INT, c4_jovem INT, c5_jovem INT, c6_jovem INT, c7_jovem INT,
                 c1_gestor INT, c2_gestor INT, c3_gestor INT, c4_gestor INT, c5_gestor INT, c6_gestor INT, c7_gestor INT,
                 status TEXT, data TEXT)''')
    conn.commit()
    conn.close()

init_db()

st.set_page_config(page_title="Sistema Pescar 2026", layout="wide")

# --- INTERFACE ---
st.sidebar.title("📌 Menu")
modo = st.sidebar.radio("Navegar:", ["Área do Aluno", "Painel do Gestor (Jorge)"])

if modo == "Área do Aluno":
    st.header("📝 Autoavaliação do Jovem")
    with st.form("form_jovem"):
        nome = st.text_input("Nome Completo:")
        etapa = st.selectbox("Etapa:", ["Etapa 1", "Etapa 2"])
        
        notas_jovem = []
        for titulo, desc in INFOS_PESCAR.items():
            st.markdown(f"### {titulo}")
            st.caption(desc)
            nota = st.radio(f"Sua nota para {titulo}:", [1, 2, 3, 4, 5], horizontal=True, key=titulo)
            notas_jovem.append(nota)
            st.write("---")
            
        if st.form_submit_button("Enviar para o Educador"):
            conn = sqlite3.connect('pescar_v3.db')
            c = conn.cursor()
            c.execute("""INSERT INTO avaliacoes (nome, etapa, c1_jovem, c2_jovem, c3_jovem, c4_jovem, c5_jovem, c6_jovem, c7_jovem, status, data) 
                         VALUES (?,?,?,?,?,?,?,?,?,?,?)""", 
                      (nome, etapa, *notas_jovem, "Pendente Gestor", datetime.now().strftime("%d/%m/%Y")))
            conn.commit()
            conn.close()
            st.success("✅ Enviado! Agora o Jorge fará a avaliação dele.")

elif modo == "Painel do Gestor (Jorge)":
    senha = st.sidebar.text_input("Senha:", type="password")
    if senha == "jorge2026":
        st.header("📊 Gestão de Avaliações")
        
        conn = sqlite3.connect('pescar_v3.db')
        df = pd.read_sql("SELECT * FROM avaliacoes", conn)
        conn.close()

        if not df.empty:
            pendentes = df[df['status'] == "Pendente Gestor"]
            
            if not pendentes.empty:
                st.subheader("⚠️ Avaliações aguardando sua nota")
                aluno_id = st.selectbox("Selecione o aluno para avaliar:", pendentes['id'].tolist(), format_func=lambda x: df[df['id']==x]['nome'].values[0])
                
                with st.form("form_gestor"):
                    notas_gestor = []
                    for titulo in INFOS_PESCAR.keys():
                        n_g = st.slider(f"Sua nota para: {titulo}", 1, 5, 3)
                        notas_gestor.append(n_g)
                    
                    if st.form_submit_button("Finalizar Avaliação"):
                        conn = sqlite3.connect('pescar_v3.db')
                        c = conn.cursor()
                        c.execute(f"""UPDATE avaliacoes SET 
                                    c1_gestor=?, c2_gestor=?, c3_gestor=?, c4_gestor=?, c5_gestor=?, c6_gestor=?, c7_gestor=?, 
                                    status='Finalizado' WHERE id=?""", (*notas_gestor, aluno_id))
                        conn.commit()
                        conn.close()
                        st.rerun()

            # --- GRÁFICOS ---
            st.write("---")
            st.subheader("📈 Resultados Finais (Média Jovem + Gestor)")
            finalizados = df[df['status'] == "Finalizado"]
            if not finalizados.empty:
                aluno_ver = st.selectbox("Ver Gráfico de:", finalizados['nome'].unique())
                dados_v = finalizados[finalizados['nome'] == aluno_ver].iloc[-1]
                
                # Cálculo da média (Jovem + Gestor) / 2
                medias_finais = [(dados_v[f'c{i}_jovem'] + dados_v[f'c{i}_gestor'])/2 for i in range(1, 8)]
                
                fig_radar = go.Figure()
                fig_radar.add_trace(go.Scatterpolar(r=medias_finais, theta=list(INFOS_PESCAR.keys()), fill='toself', name=aluno_ver))
                fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])))
                st.plotly_chart(fig_radar)
        else:
            st.info("Nenhuma avaliação registrada.")
