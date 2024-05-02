from openai import OpenAI
import json
import streamlit as st
from typing import Callable, Any

client = OpenAI(api_key=st.secrets.get("OPENAI_API_KEY"))
model = st.secrets.get("OPENAI_MODEL")

default_prompt = """
Você será identificado como Pegasus o cavalo sabichão.
Sua função será responder questões referente a transcrição de uma reunião.
Você apenas irá determinar a intenção do usuário e chamar a função adequada para responder a pergunta.
Não use seu conhecimento prévio para responder perguntas.
Apenas identifique a intenção do usuário.

Você precisa atender a três pedidos especiais de busca:

1. Quem falou "tais termos" na reunião: fazer uma busca pelo(s) termo(s)
de busca e indicar quem utilizou o(s) termo(s) em uma mesma frase, neste caso utilizar a função "get_search_term".

2. Onde foi falado sobre "tal coisa": retornar a frase que contenha a "tal
coisa" procurada, neste caso utilizar a função "get_search_things".

3. Solicitar o sentimento associado com a frase obtida no item anterior. Neste caso deverá ser observado
a frase retornada no item anterior e chamar a função "get_sentiment_analysis".
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
                "description": "Fazer uma busca pelos termos",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "terms": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "Array ou lista de strings que contém os termos a serem pesquisados",
                        }
                    },
                    "required": ["terms"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_search_things",
                "description": "Fazer uma busca pelas coisas",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "things": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "Array ou lista de strings que contém as coisas a serem pesquisados",
                        }
                    },
                    "required": ["things"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_sentiment_analysis",
                "description": "Fazer uma análise das frases anteriores retornadas pela funções de procura de termos ou de coisas",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "sentences": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "Array ou lista de strings que contém as frases a serem analisadas. Somente as frases retornadas pelas funções mencionadas.",
                        }
                    },
                    "required": ["sentences"],
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
        print("vai chamar")
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
            print("chamou", function_name, function_response)
        
        second_response = client.chat.completions.create(
            model=model,
            messages=messages,
        )

        second_response_message = second_response.choices[0].message.content

        return second_response_message
    
    else:
        return response_message.content
