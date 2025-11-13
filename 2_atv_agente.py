# Feito por: Enzo Alcantara de Santana e Luiza de Assis Fernandes.
import os
import streamlit as st
from crewai import Agent, Task, Crew, Process, LLM

# ---------------------------
# UI - Interface Streamlit
# ---------------------------
st.header("💻 MasterCode.IA ")
st.write("Descreva um problema de programação e deixe a equipe de IAs resolvê-lo.")

# Inputs do usuário
problema = st.text_area("Descreva o problema ou a função que você precisa:", 
                        placeholder="Ex.: Preciso de uma função em Python que receba um texto e conte a frequência de cada palavra, retornando um dicionário.")
linguagem = st.selectbox("Linguagem de Programação", 
                         ["Python", "JavaScript", "C#", "Java", "Outra (especificar no problema)"])

api_key = st.text_input("Sua API Key (Groq)", type="password", placeholder="gsk_...")

executar = st.button("Gerar Código")

if executar:
    if not api_key or not problema:
        st.error("Por favor, informe a API key e a descrição do problema.")
        st.stop()

    # ---------------------------
    # LLM (Groq / Llama 3)
    # ---------------------------
    llm = LLM(
        model="groq/llama-3.3-70b-versatile",
        api_key=api_key,
        temperature=0.2 # Baixa temperatura para código, queremos precisão
    )

    # ---------------------------
    # Agentes da Equipe de Devs
    # ---------------------------

    # Agente 1: Arquiteto/Planejador
    agente_arquiteto = Agent(
        role="Arquiteto de Software",
        goal=(
            "Analisar o {problema} do usuário e criar um plano técnico claro e conciso. "
            "Definir o nome da função, os parâmetros de entrada (com tipos) e o tipo de saída esperado. "
            "O plano deve ser em bullets."
        ),
        backstory=(
            "Você é um arquiteto de software sênior que se destaca em quebrar problemas complexos "
            "em requisitos técnicos simples e diretos para a equipe de desenvolvimento."
        ),
        llm=llm, verbose=False
    )

    # Agente 2: Desenvolvedor
    agente_dev = Agent(
        role=f"Desenvolvedor(a) Sênior em {linguagem}",
        goal=(
            "Escrever o código completo e funcional em {linguagem} com base no plano técnico do Arquiteto. "
            "O código deve ser limpo, eficiente e bem comentado, explicando a lógica."
        ),
        backstory=(
            f"Você é um(a) programador(a) expert em {linguagem}, focado(a) em escrever "
            "código de alta qualidade que resolve o problema proposto de forma robusta."
        ),
        llm=llm, verbose=False
    )

    # Agente 3: Engenheiro de QA (Testes)
    agente_qa = Agent(
        role="Engenheiro(a) de QA (Testes)",
        goal=(
            "Com base no código final, criar 3 casos de teste significativos para validar a função. "
            "Incluir um teste 'caminho feliz' (válido), um teste de 'borda' (edge case) "
            "e um teste 'inválido' (ex: input nulo ou formato errado)."
        ),
        backstory=(
            "Você é um engenheiro de QA detalhista, mestre em encontrar bugs e garantir "
            "que o código funcione perfeitamente em todos os cenários antes de ir para produção."
        ),
        llm=llm, verbose=False
    )

    # ---------------------------
    # Tarefas da Equipe
    # ---------------------------

    # Tarefa 1: Planejamento
    t_arquiteto = Task(
        description=(
            "PLANO TÉCNICO\n"
            "Analise este problema: {problema}. "
            "Crie um plano técnico em Markdown. "
            "Defina: 1. Nome da Função/Classe, 2. Parâmetros de Entrada (com tipos), 3. Saída Esperada (com tipo)."
        ),
        agent=agente_arquiteto,
        expected_output="Um plano técnico em Markdown com a assinatura da função e requisitos."
    )

    # Tarefa 2: Codificação
    t_dev = Task(
        description=(
            "CÓDIGO FONTE\n"
            "Usando o plano técnico do Arquiteto, escreva o código completo em {linguagem}. "
            "Formate o código final dentro de um bloco de markdown (ex: ```{linguagem} ... ```). "
            "Inclua comentários explicando partes complexas."
        ),
        agent=agente_dev,
        expected_output=f"Um único bloco de código Markdown (```{linguagem} ... ```) com a solução completa.",
        context=[t_arquiteto] # Esta tarefa DEPENDE da t_arquiteto
    )

    # Tarefa 3: Testes
    t_qa = Task(
        description=(
            "CASOS DE TESTE\n"
            "Revise o código gerado pelo Desenvolvedor. Crie 3 casos de teste em Markdown. "
            "Para cada teste (Válido, Borda, Inválido), liste: **Entrada** e **Saída Esperada**."
        ),
        agent=agente_qa,
        expected_output="Uma lista numerada em Markdown com os 3 casos de teste.",
        context=[t_dev] # Esta tarefa DEPENDE da t_dev
    )

    # ---------------------------
    # Orquestração (Crew)
    # ---------------------------
    crew = Crew(
        agents=[agente_arquiteto, agente_dev, agente_qa],
        tasks=[t_arquiteto, t_dev, t_qa],
        process=Process.sequential, # Garante que as tarefas rodem em ordem (Arquiteto -> Dev -> QA)
    )

    with st.spinner("A equipe de IAs está trabalhando... 🤖 📐 💻 🧪"):
        crew.kickoff(inputs={
            "problema": problema,
            "linguagem": linguagem
        })

    # ---------------------------
    # Exibição dos Resultados
    # ---------------------------
    
    # Extrai o resultado de cada tarefa
    plano_out = getattr(t_arquiteto, "output", None) or getattr(t_arquiteto, "result", "") or ""
    codigo_out = getattr(t_dev, "output", None) or getattr(t_dev, "result", "") or ""
    testes_out = getattr(t_qa, "output", None) or getattr(t_qa, "result", "") or ""

    # Abas para cada etapa do processo
    aba_codigo, aba_plano, aba_testes = st.tabs(
        ["✅ Código Final", "📐 Plano do Arquiteto", "🧪 Casos de Teste"]
    )

    with aba_codigo:
        st.markdown(codigo_out)
    with aba_plano:
        st.markdown(plano_out)
    with aba_testes:
        st.markdown(testes_out)