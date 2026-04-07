# ... (mantenha o início do código igual)

        # ABA 2: GRÁFICOS INDIVIDUAIS
        with tab2:
            finalizados = df[df['status'] == 'F']
            if not finalizados.empty:
                aluno = st.selectbox("Escolha o Aluno:", finalizados['nome'].unique())
                d = finalizados[finalizados['nome'] == aluno].iloc[-1]
                m_ind = [(float(d[f'j{i}'])+float(d[f'g{i}']))/2 for i in range(1,8)]
                
                col1, col2 = st.columns(2)
                with col1:
                    fig_ri = go.Figure(data=go.Scatterpolar(r=m_ind, theta=COMPETENCIAS, fill='toself', fillcolor='rgba(31, 119, 180, 0.5)'))
                    fig_ri.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), title="Radar Individual")
                    st.plotly_chart(fig_ri, use_container_width=True)
                with col2:
                    # CORREÇÃO DA COR AQUI:
                    fig_bi = px.bar(x=COMPETENCIAS, y=m_ind, title="Barras Individual", 
                                   color=m_ind, color_continuous_scale="RdYlGn", # Escala Vermelho-Amarelo-Verde
                                   range_color=[1, 5], labels={'x': 'Competência', 'y': 'Nota Final'})
                    fig_bi.update_yaxes(range=[0, 5])
                    st.plotly_chart(fig_bi, use_container_width=True)

        # ABA 3: GRÁFICOS DA TURMA
        with tab3:
            if not finalizados.empty:
                et = st.radio("Ver Turma na:", ["Etapa 1", "Etapa 2"], horizontal=True)
                df_et = finalizados[finalizados['etapa'] == et]
                if not df_et.empty:
                    m_turma = [round((df_et[f'j{i}'].mean() + df_et[f'g{i}'].mean())/2, 2) for i in range(1,8)]
                    col1, col2 = st.columns(2)
                    with col1:
                        fig_rt = go.Figure(data=go.Scatterpolar(r=m_turma, theta=COMPETENCIAS, fill='toself', line_color='#2ca02c', fillcolor='rgba(44, 160, 44, 0.5)'))
                        fig_rt.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 5])), title=f"Radar Geral - {et}")
                        st.plotly_chart(fig_rt, use_container_width=True)
                    with col2:
                        # CORREÇÃO DA COR AQUI TAMBÉM:
                        fig_bt = px.bar(x=COMPETENCIAS, y=m_turma, title=f"Barras Geral - {et}", 
                                       color=m_turma, color_continuous_scale="RdYlGn", 
                                       range_color=[1, 5], labels={'x': 'Competência', 'y': 'Média da Turma'})
                        fig_bt.update_yaxes(range=[0, 5])
                        st.plotly_chart(fig_bt, use_container_width=True)
# ... (mantenha o restante do código)
