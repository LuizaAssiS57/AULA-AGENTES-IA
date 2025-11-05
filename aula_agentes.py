import os
import streamlit as st 
from crewai import Agent, Task, Crew, Process, LLM

# AGENTE PARA ESTUDO.
st.header(" 🤖 Agentes para Estudo 📚")
st.write("Informe o tema e gere material para estudar: ")

tema = st.text_input("Tema de estudo: ", placeholder="Ex.: Algoritmos")
objetivo = st.text_input("Objetivo: ", placeholder="Ex.: Entender conceitos")

executar = st.button("Gerar material")
api_key = 'CHAVE_API'

if executar:
    llm = LLM(
        model="groq/llama-3.3-70b-versatile",
        api_key=api_key
        temperature=0.3
        # Temperature: define o nível de criatividade.
        # menor ou igual 0.3 mais determinístico
        # entre 0.4 e 0.7 equilibrado para explicação
        # maior que 0.7 mais criativo e menos previsível.
    )