import sqlite3

def conectar():
    return sqlite3.connect("pelada_stats.db", check_same_thread=False)

def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jogadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE NOT NULL,
            posicao TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS series (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero INTEGER NOT NULL,
            data_inicio DATE,
            data_fim DATE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jogos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            serie_id INTEGER NOT NULL,
            data DATE NOT NULL,
            gols_amarelo INTEGER,
            gols_vermelho INTEGER,
            vencedor TEXT,
            FOREIGN KEY (serie_id) REFERENCES series (id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS estatisticas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            jogo_id INTEGER,
            jogador_id INTEGER,
            gols INTEGER,
            assistencias INTEGER,
            cartoes_amarelos INTEGER,
            cartoes_vermelhos INTEGER DEFAULT 0,
            defesas_dificeis INTEGER,
            clean_sheet BOOLEAN,
            melhor_em_campo BOOLEAN,
            FOREIGN KEY (jogo_id) REFERENCES jogos (id),
            FOREIGN KEY (jogador_id) REFERENCES jogadores (id)
        )
    ''')

    # Índices para otimização
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_estatisticas_jogador ON estatisticas(jogador_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_jogos_serie ON jogos(serie_id)')

    conn.commit()
    conn.close()