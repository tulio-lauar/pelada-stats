import streamlit as st
import pandas as pd
from database.db import conectar

def exibir():
    st.title("📊 Estatísticas Individuais")

    conn = conectar()
    cursor = conn.cursor()

    # Buscar jogadores
    cursor.execute("SELECT id, nome FROM jogadores ORDER BY nome")
    jogadores = cursor.fetchall()

    nomes_jogadores = [j[1] for j in jogadores]
    jogador_nome = st.selectbox("Selecione o jogador", nomes_jogadores)

    jogador_id = [j[0] for j in jogadores if j[1] == jogador_nome][0]

    # Filtros adicionais
    cursor.execute("SELECT DISTINCT numero FROM series ORDER BY numero")
    series = [row[0] for row in cursor.fetchall()]
    serie = st.sidebar.selectbox("Série", options=["Todas"] + series)

    cursor.execute("SELECT DISTINCT strftime('%Y', data) FROM jogos WHERE data IS NOT NULL")
    anos = sorted(set([row[0] for row in cursor.fetchall()]))
    ano = st.sidebar.selectbox("Ano", options=["Todos"] + anos)

    cursor.execute("SELECT DISTINCT strftime('%m', data) FROM jogos WHERE data IS NOT NULL")
    meses_disponiveis = sorted(set([row[0] for row in cursor.fetchall()]))

    # Proteção caso não haja meses disponíveis ainda
    if not meses_disponiveis:
        meses_disponiveis = [f"{i:02d}" for i in range(1, 13)]

    mes = st.sidebar.selectbox("Mês", options=["Todos"] + meses_disponiveis)

    semestre = st.sidebar.selectbox("Semestre", ["Todos", "1º Semestre", "2º Semestre"])

    # --- Montar base da query ---
    query = """
        SELECT 
        jogos.data AS Data,
        series.numero AS Série,
        estatisticas.gols AS Gols,
        estatisticas.assistencias AS Assistências,
        estatisticas.cartoes_amarelos AS Cartões_Amarelos,
        estatisticas.cartoes_vermelhos AS Cartões_Vermelhos,
        estatisticas.defesas_dificeis AS Defesas_Difíceis,
        estatisticas.clean_sheet AS Clean_Sheet,
        estatisticas.melhor_em_campo AS Melhor_em_Campo
    FROM estatisticas
    JOIN jogos ON estatisticas.jogo_id = jogos.id
    JOIN series ON jogos.serie_id = series.id
    WHERE estatisticas.jogador_id = ?

    """
    params = [jogador_id]

    # Filtros
    if serie != "Todas":
        query += " AND series.numero = ?"
        params.append(serie)

    if ano != "Todos":
        query += " AND strftime('%Y', jogos.data) = ?"
        params.append(str(ano))

    if mes != "Todos":
        query += " AND strftime('%m', jogos.data) = ?"
        params.append(mes)

    if semestre == "1º Semestre":
        query += " AND CAST(strftime('%m', jogos.data) AS INTEGER) BETWEEN 1 AND 6"
    elif semestre == "2º Semestre":
        query += " AND CAST(strftime('%m', jogos.data) AS INTEGER) BETWEEN 7 AND 12"

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    if df.empty:
        st.info("Nenhum dado encontrado com os filtros selecionados.")
    else:
        st.subheader(f"Estatísticas de {jogador_nome}")
        st.dataframe(df, use_container_width=True)

        st.markdown("### Totais:")
        totais = df[[
            "Gols", "Assistências", "Cartões_Amarelos", "Cartões_Vermelhos", 
            "Defesas_Difíceis", "Clean_Sheet", "Melhor_em_Campo"
        ]].sum().astype(int)
        st.write(totais.to_frame("Total"))


        st.markdown("### Distribuição de Gols por Série:")
        df_gols = df.groupby("Série")["Gols"].sum().reset_index()
        st.bar_chart(df_gols.set_index("Série"))
