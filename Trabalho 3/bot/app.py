import streamlit as st
import time

from llm.openai import get_response_function
from lib.errors import AnalysisError
from lib.text_analysis import avaiable_analysis_functions

# Configuração da página
st.set_page_config("Transcritor", page_icon=":movie_camera:")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá, eu sou o Pegasus o assistente virtual que vai ajudá-lo com a transcrição de vídeos! O que deseja saber?"},
    ]

def write_message(role, content, save=True):
    """ Escrever a mensagem na tela """
    if save:
        st.session_state.messages.append({
            "role": role,
            "content": content
        })
    
    with st.chat_message(role):
        st.markdown(content)

def handle_submit(message):
    """ Controlar a submissão do formulário """
    with st.spinner("Pensando ..."):
        response = get_response_function(st.session_state.messages, available_functions=avaiable_analysis_functions)
        time.sleep(1)
        write_message("assistant", response)

for message in st.session_state.messages:
    write_message(message['role'], message['content'], save=False)

if prompt := st.chat_input("Em que posso ajudar?"):
    write_message('user', prompt)
    handle_submit(prompt)
