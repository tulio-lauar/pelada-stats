import streamlit as st
from app import auth, insercao, dashboard, informacoes  # Importe o novo módulo
from database.db import criar_tabelas

def main():
    # Configuração inicial
    criar_tabelas()
    st.set_page_config(page_title="Pelada Stats", layout="wide")
    
    # Inicialização do estado da sessão
    if 'pagina_atual' not in st.session_state:
        st.session_state.pagina_atual = 'dashboard'
    if 'admin_logado' not in st.session_state:
        st.session_state.admin_logado = False

    # Sidebar - Menu principal
    st.sidebar.title("⚽ Menu Principal")
    
    # Botões de navegação básica (sempre visíveis)
    if st.sidebar.button("📊 Dashboard"):
        st.session_state.pagina_atual = 'dashboard'
    
    # Seção administrativa (condicional)
    if auth.verificar_autenticacao():
        st.sidebar.markdown("---")
        st.sidebar.subheader("Área Administrativa")
        
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button("📝 Cadastrar Dados"):
                st.session_state.pagina_atual = 'cadastro'
        with col2:
            if st.button("🛠 Gerenciar Dados"):
                st.session_state.pagina_atual = 'gerenciar'
        
        st.sidebar.markdown("---")
        if st.sidebar.button("🔒 Sair"):
            st.session_state.admin_logado = False
            st.session_state.pagina_atual = 'dashboard'
            st.rerun()
    else:
        if st.sidebar.button("🔑 Acessar Admin"):
            st.session_state.pagina_atual = 'login'
    
    # Controle de páginas
    if st.session_state.pagina_atual == 'login':
        auth.exibir_login()
        st.stop()
    
    elif st.session_state.pagina_atual == 'cadastro':
        insercao.exibir()
    
    elif st.session_state.pagina_atual == 'gerenciar':
        informacoes.exibir()
    
    else:  # Página padrão (dashboard)
        dashboard.exibir()

if __name__ == "__main__":
    main()