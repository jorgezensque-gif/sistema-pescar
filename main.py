# --- ABA 2: GRÁFICOS INDIVIDUAIS (CORES FORÇADAS) ---
with col2:
    # Mapeamento de cores ultra-vibrantes
    cores_vibrantes = []
    for nota in m_ind:
        if nota < 3.0: cores_vibrantes.append('#FF0000')   # Vermelho Puro
        elif nota < 4.0: cores_vibrantes.append('#FFD700') # Ouro/Amarelo
        else: cores_vibrantes.append('#008000')            # Verde Escuro

    fig_bi = go.Figure(data=[go.Bar(
        x=COMPETENCIAS, 
        y=m_ind,
        marker=dict(color=cores_vibrantes, line=dict(color='#000000', width=1.5)), # Borda preta para destacar
        text=[f"{n:.1f}" for n in m_ind], # Coloca a nota em cima da barra
        textposition='auto',
    )])
    
    fig_bi.update_layout(
        title="<b>DESEMPENHO INDIVIDUAL (NOTAS)</b>",
        yaxis=dict(range=[0, 5.2], gridcolor='lightgrey'),
        paper_bgcolor='rgba(0,0,0,0)', # Fundo transparente
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=50, b=150),
        height=500
    )
    st.plotly_chart(fig_bi, use_container_width=True)

# --- ABA 3: GRÁFICOS DA TURMA (CORES FORÇADAS) ---
with col2:
    cores_t_vibrantes = []
    for nota in m_turma:
        if nota < 3.0: cores_t_vibrantes.append('#FF0000')
        elif nota < 4.0: cores_t_vibrantes.append('#FFD700')
        else: cores_t_vibrantes.append('#008000')

    fig_bt = go.Figure(data=[go.Bar(
        x=COMPETENCIAS, 
        y=m_turma,
        marker=dict(color=cores_t_vibrantes, line=dict(color='#000000', width=1.5)),
        text=[f"{n:.1f}" for n in m_turma],
        textposition='auto',
    )])
    
    fig_bt.update_layout(
        title=f"<b>MÉDIA GERAL DA TURMA - {et}</b>",
        yaxis=dict(range=[0, 5.2], gridcolor='lightgrey'),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=20, r=20, t=50, b=150),
        height=500
    )
    st.plotly_chart(fig_bt, use_container_width=True)
