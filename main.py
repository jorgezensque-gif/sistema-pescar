# --- ABA 2: GRÁFICOS INDIVIDUAIS (CORES VIVAS) ---
with col2:
    # Criando um mapeamento de cores manual para garantir o contraste
    cores_map = []
    for nota in m_ind:
        if nota < 3: cores_map.append('red')
        elif nota < 4: cores_map.append('orange')
        else: cores_map.append('green')

    fig_bi = go.Figure(data=[go.Bar(
        x=COMPETENCIAS, 
        y=m_ind,
        marker_color=cores_map # Aplica as cores vibrantes
    )])
    
    fig_bi.update_layout(
        title="<b>Desempenho por Competência (Individual)</b>",
        yaxis=dict(range=[0, 5], title="Nota"),
        margin=dict(l=20, r=20, t=50, b=100), # Mais espaço embaixo para o texto
        height=450
    )
    st.plotly_chart(fig_bi, use_container_width=True)

# --- ABA 3: GRÁFICOS DA TURMA (CORES VIVAS) ---
with col2:
    cores_turma = []
    for nota in m_turma:
        if nota < 3: cores_turma.append('red')
        elif nota < 4: cores_turma.append('orange')
        else: cores_turma.append('green')

    fig_bt = go.Figure(data=[go.Bar(
        x=COMPETENCIAS, 
        y=m_turma,
        marker_color=cores_turma
    )])
    
    fig_bt.update_layout(
        title=f"<b>Média Geral da Turma - {et}</b>",
        yaxis=dict(range=[0, 5], title="Média"),
        margin=dict(l=20, r=20, t=50, b=100),
        height=450
    )
    st.plotly_chart(fig_bt, use_container_width=True)
