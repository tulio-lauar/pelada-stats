import streamlit as st
from database import crud
from database.db import conectar
from datetime import date

def exibir():
    st.title("📋 Cadastro de Dados")

    aba = st.selectbox("Selecione a seção para cadastro:", 
                      ["Jogadores", "Séries", "Jogo e Estatísticas"])

    if aba == "Jogadores":
        with st.form("form_jogador"):
            nome = st.text_input("Nome do jogador")
            posicao = st.selectbox("Posição", 
                                 ["Goleiro", "Zagueiro", "Lateral", "Volante", "Meia", "Atacante"])
            
            submitted = st.form_submit_button("Adicionar Jogador")
            if submitted:
                try:
                    if crud.adicionar_jogador(nome, posicao):
                        st.success("Jogador adicionado com sucesso!")
                    else:
                        st.error("Erro: Jogador já existe!")
                except Exception as e:
                    st.error(f"Erro inesperado: {e}")

        st.subheader("👥 Jogadores Cadastrados")
        jogadores = crud.buscar_jogadores()
        if jogadores:
            cols = st.columns(3)
            for i, jogador in enumerate(jogadores):
                cols[i%3].markdown(f"**{jogador[1]}** ({jogador[2]})")

    elif aba == "Séries":
        with st.form("form_serie"):
            numero = st.number_input("Número da série", min_value=1, step=1)
            data_inicio = st.date_input("Data de início")
            data_fim = st.date_input("Data de término")
            
            submitted = st.form_submit_button("Adicionar Série")
            if submitted:
                if data_inicio > data_fim:
                    st.error("Data de início não pode ser após a data de término!")
                else:
                    crud.adicionar_serie(numero, data_inicio, data_fim)
                    st.success("Série cadastrada!")

    elif aba == "Jogo e Estatísticas":
        series = crud.buscar_series()
        jogadores = crud.buscar_jogadores()

        if not series:
            st.warning("Cadastre uma série antes de inserir jogos.")
            return

        if not jogadores:
            st.warning("Cadastre jogadores antes de inserir estatísticas.")
            return

        jogador_dict = {nome: id for id, nome, _ in jogadores}
        jogador_posicoes = {nome: pos for id, nome, pos in jogadores}

        with st.form("form_jogo", clear_on_submit=True):
            st.subheader("📅 Dados do Jogo")
            serie_selecionada = st.selectbox("Série", 
                                           [f"Série {num}" for id, num in series])
            data_jogo = st.date_input("Data do jogo")
            
            col1, col2 = st.columns(2)
            with col1:
                gols_amarelo = st.number_input("Gols do time amarelo", min_value=0)
            with col2:
                gols_vermelho = st.number_input("Gols do time vermelho", min_value=0)
            
            vencedor = st.selectbox("Vencedor", ["Amarelo", "Vermelho", "Empate"])

            st.subheader("👥 Estatísticas dos Jogadores")
            estatisticas = []
            for i in range(6):
                with st.expander(f"Jogador {i+1}"):
                    jogador_nome = st.selectbox(
                        f"Selecione o jogador {i+1}",
                        options=list(jogador_dict.keys()),
                        key=f"jogador_{i}"
                    )
                    
                    is_goleiro = (jogador_posicoes.get(jogador_nome, "").lower() == "goleiro")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        gols = st.number_input("Gols", min_value=0, key=f"gols_{i}")
                    with col_b:
                        assistencias = st.number_input("Assistências", min_value=0, key=f"ass_{i}")
                    
                    cartoes_amarelos = st.number_input("Cartões Amarelos", min_value=0, key=f"amarelo_{i}")
                    cartoes_vermelhos = st.number_input("Cartões Vermelhos", min_value=0, key=f"vermelho_{i}")
                    
                    if is_goleiro:
                        st.markdown("🧤 **Estatísticas de Goleiro**")
                        defesas_dificeis = st.number_input("Defesas Difíceis", min_value=0, key=f"defesas_{i}")
                        clean_sheet = st.checkbox("Clean Sheet", key=f"clean_{i}")
                    else:
                        defesas_dificeis = 0
                        clean_sheet = False
                    
                    melhor_em_campo = st.checkbox("Melhor em Campo", key=f"mec_{i}")
                    
                    estatisticas.append({
                        "jogador_id": jogador_dict[jogador_nome],
                        "gols": gols,
                        "assistencias": assistencias,
                        "cartoes_amarelos": cartoes_amarelos,
                        "cartoes_vermelhos": cartoes_vermelhos,
                        "defesas_dificeis": defesas_dificeis,
                        "clean_sheet": int(clean_sheet),
                        "melhor_em_campo": int(melhor_em_campo)
                    })

            submitted = st.form_submit_button("Salvar Jogo")
            
            if submitted:
                try:
                    serie_id = [id for id, num in series if f"Série {num}" == serie_selecionada][0]
                    
                    conn = None
                    try:
                        conn = conectar()
                        cursor = conn.cursor()
                        
                        cursor.execute(
                            """INSERT INTO jogos 
                            (serie_id, data, gols_amarelo, gols_vermelho, vencedor)
                            VALUES (?, ?, ?, ?, ?)""",
                            (serie_id, data_jogo, gols_amarelo, gols_vermelho, vencedor)
                        )
                        jogo_id = cursor.lastrowid
                        conn.commit()
                        
                        if not jogo_id:
                            st.error("Falha ao criar o jogo")
                            st.stop()
                        
                        for estat in estatisticas:
                            cursor.execute(
                                """INSERT INTO estatisticas 
                                (jogo_id, jogador_id, gols, assistencias, 
                                cartoes_amarelos, cartoes_vermelhos,
                                defesas_dificeis, clean_sheet, melhor_em_campo)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                                (jogo_id, estat["jogador_id"], estat["gols"], 
                                 estat["assistencias"], estat["cartoes_amarelos"],
                                 estat["cartoes_vermelhos"], estat["defesas_dificeis"],
                                 estat["clean_sheet"], estat["melhor_em_campo"])
                            )
                        
                        conn.commit()
                        st.success(f"✅ Jogo {jogo_id} salvo com sucesso!")
                        st.balloons()
                    
                    except Exception as e:
                        st.error(f"Erro ao salvar: {str(e)}")
                        if conn:
                            conn.rollback()
                    
                    finally:
                        if conn:
                            conn.close()
                
                except Exception as e:
                    st.error(f"Erro geral: {str(e)}")