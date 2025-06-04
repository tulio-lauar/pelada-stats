import sqlite3
import os
from datetime import datetime

def fazer_backup(db_path):
    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    try:
        with sqlite3.connect(db_path) as src:
            with sqlite3.connect(backup_path) as dst:
                src.backup(dst)
        print(f"Backup criado em: {backup_path}")
        return True
    except Exception as e:
        print(f"Erro ao criar backup: {e}")
        return False

def migrar_colunas_cartoes(db_path):
    if not os.path.exists(db_path):
        print(f"Arquivo '{db_path}' não encontrado.")
        return False

    if not fazer_backup(db_path):
        print("Abortando migração devido a falha no backup.")
        return False

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("PRAGMA table_info(estatisticas)")
            colunas = [col[1] for col in cursor.fetchall()]
            
            if "cartoes" in colunas and "cartoes_amarelos" not in colunas:
                print("Iniciando migração...")
                
                cursor.execute("""
                    CREATE TABLE estatisticas_nova (
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
                """)
                
                cursor.execute("""
                    INSERT INTO estatisticas_nova (
                        id, jogo_id, jogador_id, gols, assistencias, 
                        cartoes_amarelos, defesas_dificeis, clean_sheet, melhor_em_campo
                    )
                    SELECT 
                        id, jogo_id, jogador_id, gols, assistencias, 
                        cartoes, defesas_dificeis, clean_sheet, melhor_em_campo
                    FROM estatisticas
                """)
                
                cursor.execute("DROP TABLE estatisticas")
                cursor.execute("ALTER TABLE estatisticas_nova RENAME TO estatisticas")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_estatisticas_jogador ON estatisticas(jogador_id)")
                
                conn.commit()
                print("✅ Migração concluída com sucesso!")
                return True
            else:
                print("ℹ️ Migração não necessária - estrutura já atualizada")
                return True
                
    except Exception as e:
        print(f"❌ Erro durante a migração: {e}")
        return False

if __name__ == "__main__":
    db_path = "pelada_stats.db"
    success = migrar_colunas_cartoes(db_path)
    
    if success:
        print("Verificando estrutura atual...")
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(estatisticas)")
            print("\nEstrutura final da tabela 'estatisticas':")
            for col in cursor.fetchall():
                print(f"- {col[1]}: {col[2]}")
    else:
        print("A migração falhou. Consulte o backup criado.")