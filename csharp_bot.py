import os # eu uso esta biblioteca apenas para limpar a tela antes de iniciar a aplicação.
import sys # esta eu uso apenas para interromper a aplicaçao em caso de problemas.
from typing import List, Dict # server apenas para criar type hints, ou seja, para me permitir definir o tipo de retorno das funções
from dotenv import load_dotenv # uso para acessar as variáveis de ambiente.
from rich.console import Console # uso pra criar um console 'bonitinho', com cores, formatações e etc.
from rich.markdown import Markdown # também uso pra criar um console 'bonitinho', com cores, formatações e etc.
from openai import OpenAI # biblioteca oficial da Open AI para comunicação com Chat GPT.

# este bloco apenas limpa a tela antes da execução da aplicação. Ela usa cls no Windows e clear no Linux/Mac
if (os.name == "nt"):
    os.system("cls")
else:
    os.system("clear")

load_dotenv() # carrega as variáveis de ambiente que estão no arquivo .env.
console = Console() # cria a classe que eu usarei para gerar o output pro usuário.

MODELO = "gpt-4o-mini" # constante que guarda o nome do modelo que usarei sendo que escolhi este pois é mais barato.

# prompt que explica pro GPT o que eu espero dele, lembrando que o GPT contume pedir dois prompts: 
#  - um pro role System que explica o que eu espero dele
#  - e outro pro role User onde eu faço as minhas perguntas/pedidos
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

# lista de mensagens enviadas e recebidas do GPT. Serve pra manter o contexto da coversa.
historico = [{ "role": "system", "content": PROMPT }] 


# simplesmente cria uma instância da classe que eu uso pra me comunicar com a API da Open AI
def obter_open_ai_api() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        console.print("[red]Erro:[/red] A chave para uso da API da Open AI não está disponível nas variáveis do ambiente.")
        sys.exit(1)
    return OpenAI()


# função mais importante do código, pois envia o prompt pra OpenAI, recebe pedaços das resposta e os mostra na tela do console.
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

    # aqui estou usando a classe Console para mosrar um título bonitinho no início da aplicação
    console.print(Markdown("# Chat C# Bot"))

    # esta chamada usa o marcador para deixar o texto opaco, já que trata-se apenas de uma dica. 
    console.print(
        "[dim]Dica: digite 'sair' para encerrar. " \
        "Faça perguntas sobre C#, .NET, EF Core, ASP.NET, LINQ e etc [/dim]\n"
        )
    
    while True:
        try:
            # mais uma vez esto usando o console pra mostar um texto bonitinho (em negrito e na cor ciano)
            pergunta_do_usuario = console.input("[bold cyan]Faça sua pergunta [/bold cyan]: ")
        except(EOFError, KeyboardInterrupt):
            print()
            break

        if (not (pergunta_do_usuario)):
            continue

        # trecho que permite abandonar o applicativo, visto este bloco é um loop infinito.
        if (pergunta_do_usuario.lower() in {"sair", "exit", "quit"}):
            break        

        # guardando a mensagem enviada para manter o contexto da conversa
        historico.append({"role": "user", "content": pergunta_do_usuario})

        # mais um impressão bonitinha no console, deste vez em negrito e verde
        console.print("[bold green]Resposta do Jarvis[/bold green]: ", end="")

        # chamada da função que efetivamente se comunica com a API da Open AI.
        resposta = transmissao_de_resposta(open_ai_api, historico)

        # guardando a mensagem recebida para manter o contexto da conversa
        historico.append({"role": "assistant", "content": resposta})


# sem comentários né
if __name__ == "__main__":
    main()