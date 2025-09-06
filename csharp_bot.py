import os
import sys
from typing import List, Dict
from dotenv import load_dotenv
from rich.console import Console
from rich.markdown import Markdown
from openai import OpenAI

if (os.name == "nt"):
    os.system("cls")
else:
    os.system("clear")

load_dotenv()
console = Console()

MODELO = "gpt-4o-mini"
PROMPT="""
Você é um assistente SÊNIOR em C#/.NET. Responda sempre em português do Brasil.
Requisitos:
- Prefira exemplos em C# 10+/11 com .NET 6+ (ou superior quando relevante).
- Mostre snippets mínimos, compiláveis e focados no problema.
- Quando houver várias abordagens (ex.: LINQ vs. loops; EF Core vs. Dapper), compare prós/contras brevemente.
- Para erros, peça a mensagem/stack, mostre hipótese de causa e passos de diagnóstico.
- Cite nuances de versões (C#/.NET/EF Core/ASP.NET) quando afetarem a resposta.
- Seja objetivo; evite floreios.
- Recuse temas não relacionados.
"""

Mensagem = Dict[str, str]
Mensagens = [{ "role": "system", "content": PROMPT }]
historico = Mensagens


def obter_open_ai_api() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        console.print("[red]Erro:[/red] A chave para uso da API da Open AI não está disponpivel nas variáveis do ambiente.")
        sys.exit(1)
    return OpenAI()


def transmissao_de_resposta(open_ai_api: OpenAI, mensagens: List[Mensagem]) -> str:
    chat = open_ai_api.chat.completions.create(
        model=MODELO,
        messages=mensagens,
        stream=True,
        temperature=0.2
    )

    texto_completo = []

    for pedaco in chat:
        delta = pedaco.choices[0].delta
        texto = delta.content
        if delta and texto:
            console.print(texto, end="")
            texto_completo.append(texto)
    
    print()
    
    return "".join(texto_completo)
    

def main():
    open_ai_api = obter_open_ai_api()

    console.print(Markdown("# Chat C# Bot"))
    console.print(
        "[dim]Dica: digite 'sair' para encerrar. " \
        "Faça perguntas sobre C#, .NET, EF Core, ASP.NET, LINQ e etc [/dim]\n"
        )
    
    while True:
        try:
            pergunta_do_usuario = console.input("[bold cyan]Faça sua pergunta [/bold cyan]: ")
        except(EOFError, KeyboardInterrupt):
            print()
            break

        if (not (pergunta_do_usuario)):
            continue

        if (pergunta_do_usuario.lower() in {"sair", "exit", "quit"}):
            break

        historico.append({"role": "user", "content": pergunta_do_usuario})

        console.print("[bold green]Resposta do Jarvis[/bold green]: ", end="")

        resposta = transmissao_de_resposta(open_ai_api, historico)

        historico.append({"role": "assistant", "content": resposta})


if __name__ == "__main__":
    main()