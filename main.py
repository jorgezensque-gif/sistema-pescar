# --- NO TRECHO DOS GRÁFICOS INDIVIDUAIS (ABA 2) ---
with col2:
    fig_bi = px.bar(
        x=COMPETENCIAS, 
        y=m_ind, 
        title="<b>Desempenho por Competência (Individual)</b>",
        color=m_ind, 
        color_continuous_scale="RdYlGn", # Escala semáforo vibrante
        range_color=[1, 5], # Garante que o vermelho seja 1 e o verde seja 5
        labels={'x': 'Competência', 'y': 'Nota Final'}
    )
    fig_bi.update_layout(coloraxis_showscale=False) # Remove a barra lateral de legenda para limpar o visual
    fig_bi.update_yaxes(range=[0, 5.5]) # Espaço extra no topo
    st.plotly_chart(fig_bi, use_container_width=True)

# --- NO TRECHO DOS GRÁFICOS DA TURMA (ABA 3) ---
with col2:
    fig_bt = px.bar(
        x=COMPETENCIAS, 
        y=m_turma, 
        title=f"<b>Média Geral da Turma - {et}</b>", 
        color=m_turma, 
        color_continuous_scale="RdYlGn", 
        range_color=[1, 5],
        labels={'x': 'Competência', 'y': 'Média da Turma'}
    )
    fig_bt.update_layout(coloraxis_showscale=False)
    fig_bt.update_yaxes(range=[0, 5.5])
    st.plotly_chart(fig_bt, use_container_width=True)
