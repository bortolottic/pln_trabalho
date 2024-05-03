from openai import OpenAI
import json
import streamlit as st
from typing import Callable, Any

client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY"))
model = st.secrets.get("OPENAI_MODEL")

default_prompt = """
Você é um assistente que irá responder questões sobre uma transcrição de um reunião gravada.
As informações necessárias que você irá obter será através de funções fornecidas.
Você será identificado como Pegasus o cavalo sabichão.
Você apenas irá determinar a intenção do usuário e chamar a função adequada para responder a pergunta.
Use somente o idioma português do Brasil.
Não use seu conhecimento prévio para responder perguntas, use apenas o que será fornecido através das funções (Ferramentas) no seu contexto.
As funções sempre irão retornar as frases no formato padrão de transcrição, conforme abaixo entre aspas triplas, caso ela encontre os termos, caso não encontre o termo ela irá retornar apenas "<NOT_FOUND>".
```
[ TEMPO INÍCIO - TEMPO FIM ] PESSOA : TEXTO
```

Você precisa atender aos seguintes pedidos especiais:

1. Quem falou "tais termos" na reunião: fazer uma busca pelo(s) termo(s)
de busca e indicar quem utilizou o(s) termo(s) em uma mesma frase.

2. Onde foi falado sobre "tal coisa": retornar a frase que contenha a "tal
coisa" procurada.

3. Solicitar o sentimento referente a(s) frase(s) obtida(s) na chamada anterior.

"""

def get_response_function(context_messages : list, available_functions : dict) -> str:
    """
    Identificar a itenção do usuário e disparar a função adequada.
    """
    messages = [
        {
            "role": "system",
            "content": default_prompt
        }
    ]

    messages.extend(context_messages[-5:]) # Somente as últimas 5 mensagens

    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_search_term",
                "description": "Localizar quem falou mais os termos informados pelo usuário",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "terms": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "Array que contém os termos a serem pesquisados",
                        }
                    },
                    "required": ["terms"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_sentiment_analysis",
                "description": "Fazer uma análise de sentimento referente a última frase contida no histórico da conversa. O retorno desta função será um json contendo as chaves: neg para % negativo, neu para % neutro, pos para % positivo e compound.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "sentence": {
                            "type": "string",                            
                            "description": "A frase a ser analisada.",
                        }
                    },
                    "required": ["sentence"],
                },
            },
        },
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
        
    if tool_calls:
        messages.append(response_message)

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            function_response = function_to_call(**function_args)
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )
        
        # second_response = client.chat.completions.create(
        #     model=model,
        #     messages=messages,
        # )

        # second_response_message = second_response.choices[0].message.content

        # return second_response_message
        return get_response_function(messages, available_functions)
    
    else:
        return response_message.content
