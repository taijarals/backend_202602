import streamlit as st

st.title("Projeto Educacional")

nome = st.text_input("Nome")

if st.button("Cadastrar"):

    st.success(
        f"{nome} cadastrado"
    )