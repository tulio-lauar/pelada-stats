import streamlit as st
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv()

def verificar_autenticacao():
    
    if 'admin_logado' not in st.session_state:
        st.session_state.admin_logado = False
    return st.session_state.admin_logado

def exibir_login():
    st.title("🔐 Login Administrativo")
    
    
    with st.container():
        senha = st.text_input("Senha:", type="password", key="senha_admin_input")
        
        
        if st.button("Entrar", key="login_btn"):
            if senha == os.getenv("ADMIN_PASSWORD"):  
                st.session_state.admin_logado = True
                st.success("Login realizado com sucesso!")
                st.rerun()  
            else:
                st.error("Senha incorreta!")
                st.session_state.admin_logado = False