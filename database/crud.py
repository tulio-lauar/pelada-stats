import sqlite3
import pandas as pd
from database.db import conectar

# ===== OPERAÇÕES COMUNS =====
def executar_query(query, params=()):
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        return cursor.lastrowid

# ===== JOGADORES =====
def adicionar_jogador(nome, posicao):
    try:
        with conectar() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO jogadores (nome, posicao) VALUES (?, ?)",
                (nome, posicao)
            )
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        return False
    except Exception as e:
        print(f"Erro ao adicionar jogador: {str(e)}")
        return False

def buscar_jogadores():
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, posicao FROM jogadores ORDER BY nome")
        return cursor.fetchall()  # Retorna lista de tuplas ao invés de DataFrame

def atualizar_jogador(jogador_id, novo_nome, nova_posicao):
    try:
        executar_query(
            "UPDATE jogadores SET nome = ?, posicao = ? WHERE id = ?",
            (novo_nome, nova_posicao, jogador_id)
        )
        return True
    except Exception as e:
        print(f"Erro ao atualizar jogador: {str(e)}")
        return False

def excluir_jogador(jogador_id):
    try:
        executar_query("DELETE FROM jogadores WHERE id = ?", (jogador_id,))
        return True
    except Exception as e:
        print(f"Erro ao excluir jogador: {str(e)}")
        return False

# ===== SÉRIES =====
def adicionar_serie(numero, data_inicio, data_fim):
    try:
        executar_query(
            "INSERT INTO series (numero, data_inicio, data_fim) VALUES (?, ?, ?)",
            (numero, data_inicio, data_fim)
        )
        return True
    except Exception as e:
        print(f"Erro ao adicionar série: {str(e)}")
        return False

def buscar_series():
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, numero FROM series ORDER BY numero")
        return cursor.fetchall()  # Retorna lista de tuplas (id, numero)

def atualizar_serie(serie_id, novo_numero, nova_data_inicio, nova_data_fim):
    try:
        executar_query(
            """UPDATE series 
            SET numero = ?, data_inicio = ?, data_fim = ? 
            WHERE id = ?""",
            (novo_numero, nova_data_inicio, nova_data_fim, serie_id)
        )
        return True
    except Exception as e:
        print(f"Erro ao atualizar série: {str(e)}")
        return False

def excluir_serie(serie_id):
    try:
        executar_query("DELETE FROM series WHERE id = ?", (serie_id,))
        return True
    except Exception as e:
        print(f"Erro ao excluir série: {str(e)}")
        return False

# ===== JOGOS =====
def adicionar_jogo(serie_id, data, gols_amarelo, gols_vermelho, vencedor):
    try:
        return executar_query(
            """INSERT INTO jogos 
            (serie_id, data, gols_amarelo, gols_vermelho, vencedor)
            VALUES (?, ?, ?, ?, ?)""",
            (serie_id, data, gols_amarelo, gols_vermelho, vencedor)
        )
    except Exception as e:
        print(f"Erro ao adicionar jogo: {str(e)}")
        return None

def buscar_jogos():
    with conectar() as conn:
        return pd.read_sql("SELECT * FROM jogos ORDER BY data DESC", conn)

def buscar_jogos_completos():
    with conectar() as conn:
        return pd.read_sql("""
            SELECT j.*, s.numero as serie_numero 
            FROM jogos j
            JOIN series s ON j.serie_id = s.id
            ORDER BY j.data DESC
        """, conn)

def atualizar_jogo(jogo_id, serie_id, data, gols_amarelo, gols_vermelho, vencedor):
    try:
        executar_query(
            """UPDATE jogos 
            SET serie_id = ?, data = ?, gols_amarelo = ?, 
                gols_vermelho = ?, vencedor = ?
            WHERE id = ?""",
            (serie_id, data, gols_amarelo, gols_vermelho, vencedor, jogo_id)
        )
        return True
    except Exception as e:
        print(f"Erro ao atualizar jogo: {str(e)}")
        return False

def excluir_jogo(jogo_id):
    try:
        with conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM estatisticas WHERE jogo_id = ?", (jogo_id,))
            cursor.execute("DELETE FROM jogos WHERE id = ?", (jogo_id,))
            conn.commit()
        return True
    except Exception as e:
        print(f"Erro ao excluir jogo: {str(e)}")
        return False

# ===== ESTATÍSTICAS =====
def adicionar_estatistica(jogo_id, jogador_id, gols, assistencias, 
                         cartoes_amarelos, cartoes_vermelhos, 
                         defesas_dificeis, clean_sheet, melhor_em_campo):
    try:
        executar_query(
            """INSERT INTO estatisticas 
            (jogo_id, jogador_id, gols, assistencias,
             cartoes_amarelos, cartoes_vermelhos,
             defesas_dificeis, clean_sheet, melhor_em_campo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (jogo_id, jogador_id, gols, assistencias, 
             cartoes_amarelos, cartoes_vermelhos,
             defesas_dificeis, int(clean_sheet), int(melhor_em_campo))
        )
        return True
    except Exception as e:
        print(f"Erro ao adicionar estatística: {str(e)}")
        return False

def buscar_estatisticas():
    with conectar() as conn:
        return pd.read_sql("SELECT * FROM estatisticas ORDER BY id DESC", conn)

def buscar_estatisticas_completas():
    with conectar() as conn:
        return pd.read_sql("""
            SELECT e.*, j.nome as jogador, s.numero as serie
            FROM estatisticas e
            JOIN jogadores j ON e.jogador_id = j.id
            JOIN jogos g ON e.jogo_id = g.id
            JOIN series s ON g.serie_id = s.id
            ORDER BY e.id DESC
        """, conn)

def atualizar_estatistica(estatistica_id, jogo_id, jogador_id, gols, assistencias,
                         cartoes_amarelos, cartoes_vermelhos, 
                         defesas_dificeis, clean_sheet, melhor_em_campo):
    try:
        executar_query(
            """UPDATE estatisticas 
            SET jogo_id = ?, jogador_id = ?, gols = ?, assistencias = ?,
                cartoes_amarelos = ?, cartoes_vermelhos = ?,
                defesas_dificeis = ?, clean_sheet = ?, melhor_em_campo = ?
            WHERE id = ?""",
            (jogo_id, jogador_id, gols, assistencias,
             cartoes_amarelos, cartoes_vermelhos,
             defesas_dificeis, int(clean_sheet), int(melhor_em_campo), estatistica_id)
        )
        return True
    except Exception as e:
        print(f"Erro ao atualizar estatística: {str(e)}")
        return False

def excluir_estatistica(estatistica_id):
    try:
        executar_query("DELETE FROM estatisticas WHERE id = ?", (estatistica_id,))
        return True
    except Exception as e:
        print(f"Erro ao excluir estatística: {str(e)}")
        return False