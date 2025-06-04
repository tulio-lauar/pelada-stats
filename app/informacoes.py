import streamlit as st
import pandas as pd
from database import crud
from database.db import conectar

def exibir():
    st.title("📋 Gerenciamento Completo")
    
    # Configuração de estilo
    st.markdown("""
        <style>
            .stDataFrame { width: 100%; }
            .stTabs [data-baseweb="tab-list"] { gap: 0.5rem; }
            .st-expander { border: 1px solid #e0e0e0; border-radius: 8px; padding: 1rem; }
            button { transition: all 0.3s ease; }
            button:hover { transform: scale(1.02); }
        </style>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3, tab4 = st.tabs(["👥 Jogadores", "🗓 Séries", "⚽ Jogos", "📊 Estatísticas"])

    # === ABA JOGADORES ===
    with tab1:
        st.header("Jogadores Cadastrados")
        with conectar() as conn:
            jogadores = pd.read_sql("SELECT * FROM jogadores ORDER BY nome", conn)
        
        if not jogadores.empty:
            st.dataframe(jogadores, use_container_width=True, hide_index=True,
                        column_config={
                            "id": "ID",
                            "nome": "Nome",
                            "posicao": "Posição"
                        })
            
            col1, col2 = st.columns(2)
            
            # --- Edição ---
            with col1:
                with st.expander("✏️ Editar Jogador", expanded=True):
                    selected_id = st.selectbox(
                        "Selecione o jogador",
                        jogadores["id"],
                        format_func=lambda x: jogadores[jogadores["id"]==x]["nome"].values[0],
                        key="edit_jogador"
                    )
                    
                    jogador = jogadores[jogadores["id"]==selected_id].iloc[0]
                    
                    novo_nome = st.text_input("Nome", value=jogador["nome"], key="nome_jogador")
                    nova_posicao = st.selectbox(
                        "Posição", 
                        ["Goleiro", "Zagueiro", "Lateral", "Volante", "Meia", "Atacante"],
                        index=["Goleiro", "Zagueiro", "Lateral", "Volante", "Meia", "Atacante"].index(jogador["posicao"]),
                        key="pos_jogador"
                    )
                    
                    if st.button("💾 Salvar Alterações", key="save_jogador"):
                        try:
                            crud.atualizar_jogador(selected_id, novo_nome, nova_posicao)
                            st.success("Jogador atualizado com sucesso!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao atualizar: {str(e)}")
            
            # --- Exclusão ---
            with col2:
                with st.expander("❌ Excluir Jogador", expanded=True):
                    delete_id = st.selectbox(
                        "Selecione para excluir",
                        jogadores["id"],
                        format_func=lambda x: jogadores[jogadores["id"]==x]["nome"].values[0],
                        key="del_jogador"
                    )
                    
                    if st.button("🗑️ Confirmar Exclusão", key="confirm_del_jogador"):
                        try:
                            crud.excluir_jogador(delete_id)
                            st.success("Jogador excluído permanentemente!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao excluir: {str(e)}")
        else:
            st.info("Nenhum jogador cadastrado ainda.", icon="ℹ️")

    # === ABA SÉRIES ===
    with tab2:
        st.header("Séries Cadastradas")
        with conectar() as conn:
            series = pd.read_sql("SELECT * FROM series ORDER BY numero", conn)
        
        if not series.empty:
            st.dataframe(series, use_container_width=True, hide_index=True,
                        column_config={
                            "id": "ID",
                            "numero": "Número",
                            "data_inicio": "Data Início",
                            "data_fim": "Data Fim"
                        })
            
            col1, col2 = st.columns(2)
            
            # --- Edição ---
            with col1:
                with st.expander("✏️ Editar Série", expanded=True):
                    selected_id = st.selectbox(
                        "Selecione a série",
                        series["id"],
                        format_func=lambda x: f"Série {series[series['id']==x]['numero'].values[0]}",
                        key="edit_serie"
                    )
                    
                    serie = series[series["id"]==selected_id].iloc[0]
                    
                    novo_numero = st.number_input("Número", value=serie["numero"], min_value=1, key="num_serie")
                    nova_data_inicio = st.date_input("Data Início", value=pd.to_datetime(serie["data_inicio"]), key="dt_ini_serie")
                    nova_data_fim = st.date_input("Data Fim", value=pd.to_datetime(serie["data_fim"]), key="dt_fim_serie")
                    
                    if st.button("💾 Salvar Alterações", key="save_serie"):
                        try:
                            crud.atualizar_serie(selected_id, novo_numero, nova_data_inicio, nova_data_fim)
                            st.success("Série atualizada com sucesso!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao atualizar: {str(e)}")
            
            # --- Exclusão ---
            with col2:
                with st.expander("❌ Excluir Série", expanded=True):
                    delete_id = st.selectbox(
                        "Selecione para excluir",
                        series["id"],
                        format_func=lambda x: f"Série {series[series['id']==x]['numero'].values[0]}",
                        key="del_serie"
                    )
                    
                    if st.button("🗑️ Confirmar Exclusão", key="confirm_del_serie"):
                        try:
                            crud.excluir_serie(delete_id)
                            st.success("Série excluída permanentemente!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao excluir: {str(e)}")
        else:
            st.info("Nenhuma série cadastrada ainda.", icon="ℹ️")

    # === ABA JOGOS === 
    with tab3:
        st.header("Jogos Cadastrados")
        with conectar() as conn:
            jogos = pd.read_sql("""
                SELECT j.id, j.data, s.numero as serie, 
                       j.gols_amarelo, j.gols_vermelho, j.vencedor
                FROM jogos j
                JOIN series s ON j.serie_id = s.id
                ORDER BY j.data DESC
            """, conn)
        
        if not jogos.empty:
            st.dataframe(jogos, use_container_width=True, hide_index=True,
                        column_config={
                            "id": "ID",
                            "data": "Data",
                            "serie": "Série",
                            "gols_amarelo": "Gols Time Amarelo",
                            "gols_vermelho": "Gols Time Vermelho",
                            "vencedor": "Vencedor"
                        })
            
            col1, col2 = st.columns(2)
            
            # --- Edição ---
            with col1:
                with st.expander("✏️ Editar Jogo", expanded=True):
                    selected_id = st.selectbox(
                        "Selecione o jogo",
                        jogos["id"],
                        format_func=lambda x: f"Jogo {x} - {jogos[jogos['id']==x]['data'].values[0]}",
                        key="edit_jogo"
                    )
                    
                    jogo = jogos[jogos["id"]==selected_id].iloc[0]
                    
                    # Formulário de edição (implemente similar às abas anteriores)
                    # ...
            
            # --- Exclusão ---
            with col2:
                with st.expander("❌ Excluir Jogo", expanded=True):
                    delete_id = st.selectbox(
                        "Selecione para excluir",
                        jogos["id"],
                        format_func=lambda x: f"Jogo {x} - {jogos[jogos['id']==x]['data'].values[0]}",
                        key="del_jogo"
                    )
                    
                    if st.button("🗑️ Confirmar Exclusão", key="confirm_del_jogo"):
                        try:
                            crud.excluir_jogo(delete_id)
                            st.success("Jogo excluído permanentemente!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao excluir: {str(e)}")
        else:
            st.info("Nenhum jogo cadastrado ainda.", icon="ℹ️")

    # === ABA ESTATÍSTICAS ===
    with tab4:
        st.header("Estatísticas dos Jogadores")
        with conectar() as conn:
            estatisticas = pd.read_sql("""
                SELECT e.id, j.nome as jogador, e.gols, e.assistencias,
                       e.cartoes_amarelos, e.cartoes_vermelhos, e.defesas_dificeis,
                       e.clean_sheet, e.melhor_em_campo, s.numero as serie
                FROM estatisticas e
                JOIN jogadores j ON e.jogador_id = j.id
                JOIN jogos jo ON e.jogo_id = jo.id
                JOIN series s ON jo.serie_id = s.id
                ORDER BY e.id DESC
            """, conn)
        
        if not estatisticas.empty:
            st.dataframe(estatisticas, use_container_width=True, hide_index=True)
            
            col1, col2 = st.columns(2)
            
            # --- Edição ---
            with col1:
                with st.expander("✏️ Editar Estatística", expanded=True):
                    # Implemente similar às abas anteriores
                    pass
            
            # --- Exclusão ---
            with col2:
                with st.expander("❌ Excluir Estatística", expanded=True):
                    delete_id = st.number_input(
                        "ID da estatística para excluir",
                        min_value=1,
                        step=1,
                        key="del_estat_id"
                    )
                    
                    if st.button("🗑️ Confirmar Exclusão", key="confirm_del_estat"):
                        try:
                            crud.excluir_estatistica(delete_id)
                            st.success("Estatística excluída permanentemente!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Erro ao excluir: {str(e)}")
        else:
            st.info("Nenhuma estatística cadastrada ainda.", icon="ℹ️")