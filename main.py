import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import sqlite3
from datetime import datetime
import io

# --- CONFIGURAÇÃO DAS COMPETÊNCIAS ---
COMPETENCIAS = [
    "1-SER PROTAGONISTA", "2-SER RESPONSÁVEL E COMPROMETIDO", 
    "3-COMPREENDER CONTEXTOS E COMUNICAR-SE", "4-SER DEMOCRÁTICO, ÉTICO E CIDADÃO", 
    "5-RESOLVER SITUAÇÕES PROBLEMA", "6-TRABALHAR E PRODUZIR EM EQUIPE", 
    "7-APRENDER A APRENDER"
]

def init_db():
    conn = sqlite3.connect('pescar_v12_final.db')
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

st.sidebar.title("📌 Menu de Navegação")
modo = st.sidebar.radio("Selecione a Área:", ["Aluno (Responder)", "Gestor (Jorge)"])

# --- 1. ÁREA DO ALUNO ---
if modo == "Aluno (Responder)":
    st.header("📝 Autoavaliação do Jovem")
    with st.form("form_aluno", clear_on_submit=True):
        nome = st.text_input("Nome Completo:")
        etapa = st.selectbox("Selecione a Etapa:", ["Etapa 1", "Etapa 2"])
        
        notas_j = []
        for c in COMPETENCIAS:
            st.write(f"**{c}**")
            n = st.radio("Sua nota (1-5):", [1, 2, 3, 4, 5], index=None, horizontal=True, key=f"al_{c}")
            notas_j.append(n)
            st.write("---")
            
        if st.form_submit_button("ENVIAR MINHA AVALIAÇÃO"):
            if nome and all(v is not None for v in notas_j):
                conn = sqlite3.connect('pescar_v12_final.db')
                c = conn.cursor()
                c.execute("INSERT INTO avaliacoes (nome, etapa, j1,j2,j3,j4,j5,j6,j7, status, data) VALUES (?,?,?,?,?,?,?,?,?,?,?)", 
                          (nome, etapa, *notas_j, "Pendente", datetime.now().strftime("%d/%m/%Y")))
                conn.commit()
                conn.close()
                st.success("✅ Enviado! Suas notas estão em branco para o Jorge avaliar.")
            else: st.error("❌ Erro: Preencha o nome e TODAS as notas.")

# --- 2. PAINEL DO GESTOR ---
elif modo == "Gestor (Jorge)":
    senha = st.sidebar.text_input("Senha de Acesso:", type="password")
    
    if senha == "jorge2026":
        st.header("📊 Painel de Controle - Educador Jorge")
        
        conn = sqlite3.connect('pescar_v12_final.db')
        df = pd.read_sql("SELECT * FROM avaliacoes", conn)
        conn.close()

        if df.empty:
            st.info("Aguardando as primeiras respostas dos alunos.")
        else:
            aba1, aba2, aba3, aba4 = st.tabs(["⭐ Avaliar Alunos", "👤 Resultados Individuais", "👥 Resultados da Turma", "📥 Exportar e Limpar"])

            # --- ABA 1: DAR NOTA DO GESTOR ---
            with aba1:
                pendentes = df[df['status'] == "Pendente"]
                if not pendentes.empty:
                    id_al = st.selectbox("Selecione o aluno para avaliar:", pendentes['id'].tolist(), 
                                           format_func=lambda x: df[df['id']==x]['nome'].values[0])
                    with st.form("f_gestor"):
                        notas_g = []
                        for c in COMPETENCIAS:
                            ng = st.radio(f"Nota Jorge para {c}:", [1, 2, 3, 4, 5], index=None, horizontal=True)
                            notas_g.append(ng)
                        if st.form_submit_button("FINALIZAR AVALIAÇÃO"):
                            if all(v is not None for v in notas_g):
                                conn = sqlite3.connect('pescar_v12_final.db')
                                c = conn.cursor()
                                c.execute(f"UPDATE avaliacoes SET g1=?,g2=?,g3=?,g4=?,g5=?,g6=?,g7=?, status='F' WHERE id={id_al}", (*notas_g,))
                                conn.commit()
                                conn.close()
                                st.success("Avaliação finalizada!")
                                st.rerun()
                            else: st.error("Preencha todas as notas.")
                else: st.success("Tudo em dia! Nenhum aluno pendente.")

            # --- ABA 2: GRÁFICOS INDIVIDUAIS ---
            with aba2:
                finalizados = df[df['status'] == 'F']
                if not finalizados.empty:
                    aluno_sel = st.selectbox("Ver gráficos de:", finalizados['nome'].unique())
                    dados = finalizados[finalizados['nome'] == aluno_sel].iloc[-1]
                    medias_ind = [(float(dados[f'j{i}']) + float(dados[f'g{i}']))/2 for i in range(1,8)]
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        fig_ri = go.Figure(data=go.Scatterpolar(r=medias_ind, theta=COMPETENCIAS, fill='toself'))
                        fig_ri.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), title="Radar Individual")
                        st.plotly_chart(fig_ri, use_container_width=True)
                    with c2:
                        fig_bi = px.bar(x=COMPETENCIAS, y=medias_ind, labels={'x':'','y':'Nota'}, title="Barras Individual", color=medias_ind, color_continuous_scale="RdYlGn")
                        fig_bi.update_yaxes(range=[0, 5])
                        st.plotly_chart(fig_bi, use_container_width=True)
                else: st.info("Finalize uma avaliação para ver o gráfico individual.")

            # --- ABA 3: GRÁFICOS DA TURMA ---
            with aba3:
                if not finalizados.empty:
                    etapa_f = st.radio("Filtrar Turma por:", ["Etapa 1", "Etapa 2"], horizontal=True)
                    df_t = finalizados[finalizados['etapa'] == etapa_f]
                    
                    if not df_t.empty:
                        medias_t = []
                        for i in range(1,8):
                            m = (df_t[f'j{i}'].mean() + df_t[f'g{i}'].mean()) / 2
                            medias_t.append(round(m, 2))
                        
                        c1, c2 = st.columns(2)
                        with c1:
                            fig_rt = go.Figure(data=go.Scatterpolar(r=medias_t, theta=COMPETENCIAS, fill='toself', line_color='red'))
                            fig_rt.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), title=f"Radar Geral - {etapa_f}")
                            st.plotly_chart(fig_rt, use_container_width=True)
                        with c2:
                            fig_bt = px.bar(x=COMPETENCIAS, y=medias_t, title=f"Barras Geral - {etapa_f}", color=medias_t, range_y=[0,5])
                            st.plotly_chart(fig_bt, use_container_width=True)
                    else: st.warning(f"Sem dados finalizados para a {etapa_f}")

            # --- ABA 4: EXPORTAR E LIMPAR ---
            with aba4:
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='Avaliacoes')
                st.download_button("📥 BAIXAR EXCEL (TURMA COMPLETA)", data=output.getvalue(), file_name="relatorio_pescar.xlsx")
                
                st.write("---")
                if st.button("🔴 APAGAR TODOS OS DADOS"):
                    conn = sqlite3.connect('pescar_v12_final.db')
                    conn.execute("DELETE FROM avaliacoes")
                    conn.commit()
                    conn.close()
                    st.success("Tudo limpo!")
                    st.rerun()
    elif senha_input := "": pass
    else: st.sidebar.error("Senha incorreta")
