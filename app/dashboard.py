import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime

def conectar():
    return sqlite3.connect("pelada_stats.db")

def plotar_barra(df, coluna, titulo, cor="#1f77b4"):
    fig = px.bar(df, x="nome", y=coluna, title=titulo, text_auto=True, color_discrete_sequence=[cor])
    fig.update_layout(xaxis_title="Jogador", yaxis_title=coluna)
    st.plotly_chart(fig, use_container_width=True)

def mostrar_ultimos_jogos(conn, serie_filtro, ano_filtro):
    st.header("⏱ Últimos Resultados")
    query = """
        SELECT 
            s.numero as serie,
            j.data,
            j.gols_amarelo,
            j.gols_vermelho,
            j.vencedor
        FROM jogos j
        JOIN series s ON j.serie_id = s.id
        WHERE 1=1
    """
    params = []
    
    if serie_filtro != "Todas":
        query += " AND s.numero = ?"
        params.append(int(serie_filtro.split()[1]))
    
    if ano_filtro != "Todos":
        query += " AND strftime('%Y', j.data) = ?"
        params.append(ano_filtro)
    
    query += " ORDER BY j.data DESC LIMIT 5"
    
    jogos = pd.read_sql_query(query, conn, params=params)
    
    if not jogos.empty:
        cols = st.columns(5)
        for idx, row in jogos.iterrows():
            with cols[idx % 5]:
                st.metric(
                    label=f"Série {row['serie']} | {row['data']}",
                    value=f"{row['gols_amarelo']}x{row['gols_vermelho']}",
                    delta=f"Vencedor: {row['vencedor']}"
                )
    else:
        st.info("Nenhum jogo encontrado")

def exibir():
    with conectar() as conn:
        st.title("📊 Dashboard de Estatísticas")

        # --- Filtros Avançados ---
        st.sidebar.header("Filtros")
        
        # Série
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT numero FROM series ORDER BY numero")
        series = [f"Série {row[0]}" for row in cursor.fetchall()]
        serie_filtro = st.sidebar.selectbox("Série", ["Todas"] + series)
        
        # Ano
        cursor.execute("SELECT DISTINCT strftime('%Y', data) FROM jogos ORDER BY data DESC")
        anos = [row[0] for row in cursor.fetchall() if row[0]]
        ano_filtro = st.sidebar.selectbox("Ano", ["Todos"] + anos)
        
        # Jogador
        cursor.execute("SELECT nome FROM jogadores ORDER BY nome")
        jogadores = [row[0] for row in cursor.fetchall()]
        jogador_filtro = st.sidebar.selectbox("Jogador", ["Todos"] + jogadores)

        # --- Seção de Últimos Jogos ---
        mostrar_ultimos_jogos(conn, serie_filtro, ano_filtro)

        # --- Query Principal ---
        query = """
            SELECT 
                j.nome,
                j.posicao,
                SUM(e.gols) as gols,
                SUM(e.assistencias) as assistencias,
                SUM(e.gols + e.assistencias) as participacoes,
                SUM(e.cartoes_amarelos) as cartoes_amarelos,
                SUM(e.cartoes_vermelhos) as cartoes_vermelhos,
                SUM(e.defesas_dificeis) as defesas_dificeis,
                SUM(e.clean_sheet) as clean_sheet,
                SUM(e.melhor_em_campo) as melhor_em_campo
            FROM estatisticas e
            JOIN jogadores j ON e.jogador_id = j.id
            JOIN jogos ON e.jogo_id = jogos.id
            JOIN series s ON jogos.serie_id = s.id
            WHERE 1=1
        """
        params = []

        if serie_filtro != "Todas":
            query += " AND s.numero = ?"
            params.append(int(serie_filtro.split()[1]))
        
        if ano_filtro != "Todos":
            query += " AND strftime('%Y', jogos.data) = ?"
            params.append(ano_filtro)
            
        if jogador_filtro != "Todos":
            query += " AND j.nome = ?"
            params.append(jogador_filtro)
            
        query += " GROUP BY j.nome, j.posicao"
        
        resumo_df = pd.read_sql_query(query, conn, params=params)

        # --- Visualizações ---
        if not resumo_df.empty:
            st.markdown("---")
            
            # Novo Gráfico: Participações em Gols
            st.subheader("🎯 Participações em Gols (Gols + Assistências)")
            plotar_barra(resumo_df.sort_values("participacoes", ascending=False), 
                        "participacoes", "", "#00CC96")
            
            # Gráficos Principais
            col1, col2 = st.columns(2)
            with col1:
                plotar_barra(resumo_df, "gols", "⚽ Gols", "#1f77b4")
            with col2:
                plotar_barra(resumo_df, "assistencias", "🅰️ Assistências", "#FFA15A")
            
            # Seção para Goleiros
            goleiros_df = resumo_df[resumo_df["posicao"].str.lower() == "goleiro"]
            if not goleiros_df.empty:
                st.markdown("---")
                st.subheader("🧤 Estatísticas de Goleiros")
                col3, col4 = st.columns(2)
                with col3:
                    plotar_barra(goleiros_df, "defesas_dificeis", "🔴 Defesas Difíceis", "#EF553B")
                with col4:
                    plotar_barra(goleiros_df, "clean_sheet", "🛡️ Clean Sheets", "#00CC96")
        else:
            st.warning("Nenhum dado encontrado com os filtros selecionados")

if __name__ == "__main__":
    exibir()