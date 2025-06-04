import streamlit as st

def verificar_autenticacao():
    return st.session_state.get("admin_logado", False)
