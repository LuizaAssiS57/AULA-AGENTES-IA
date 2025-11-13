import os
import streamlit as st
from crewai import Agent, Task, Crew, Process, LLM

# ---------------------------
# UI - Interface de Marketing
# ---------------------------
st.header("🚀 Gerador de Conteúdo de Marketing")
st.write("Descreva seu produto e gere automaticamente textos para anúncios, posts e mais.")

# Inputs focados em marketing
produto = st.text_input("Nome do Produto/Serviço", placeholder="Ex.: Tênis de corrida 'Velocity'")
publico_alvo = st.text_input("Público-alvo", placeholder="Ex.: Corredores iniciantes, 20-35 anos")
beneficios = st.text_area("Principais Benefícios/Diferenciais", placeholder="Ex.: Leve, amortecimento responsivo, ótimo custo-benefício")
tom_de_voz = st.selectbox(
    "Tom de Voz da Marca",
    ["Profissional", "Amigável", "Divertido", "Urgente", "Inspirador", "Técnico"],
    index=1 # Padrão "Amigável"
)

api_key = st.text_input("Sua API Key (Groq)", type="password", placeholder="gsk_...")

executar = st.button("Gerar Conteúdo de Marketing")

if executar:
    if not api_key or not produto or not publico_alvo or not beneficios:
        st.error("Por favor, preencha a API Key, Produto, Público-alvo e Benefícios.")
        st.stop()

    # ---------------------------
    # LLM (Mantendo Groq / Llama 3)
    # ---------------------------
    llm = LLM(
        model="groq/llama-3.3-70b-versatile",
        api_key=api_key,
        temperature=0.4 
    )

    # ---------------------------
    # Agentes da Equipe de Marketing
    # ---------------------------

    # Agente 1: Focado em Branding (Slogans e CTAs)
    agente_branding = Agent(
        role="Estrategista de Marca (Branding)",
        goal=(
            "Criar 5 slogans curtos e 5 chamadas para ação (CTAs) impactantes para {produto}, "
            "usando o tom de voz {tom_de_voz} e focado nos {beneficios}."
        ),
        backstory=(
            "Você é um especialista em branding e consegue resumir o valor de "
            "um produto em frases curtas e memoráveis que geram ação."
        ),
        llm=llm, verbose=False
    )

    # Agente 2: Focado em Anúncios Pagos (PPC)
    agente_copywriter = Agent(
        role="Copywriter de Performance (PPC)",
        goal=(
            "Escrever textos persuasivos para anúncios (Google Ads e Facebook Ads) "
            "para {produto}, mirando em {publico_alvo}."
        ),
        backstory=(
            "Você é mestre em criar anúncios de alta conversão que capturam "
            "a atenção e convencem o {publico_alvo} a clicar, destacando os {beneficios}."
        ),
        llm=llm, verbose=False
    )

    # Agente 3: Focado em Mídias Sociais
    agente_social = Agent(
        role="Gerente de Mídias Sociais (Social Media)",
        goal=(
            "Gerar 3 ideias de posts criativos (Instagram/LinkedIn) para {produto}, "
            "alinhados ao {tom_de_voz} e {publico_alvo}."
        ),
        backstory=(
            "Você sabe como criar conteúdo que engaja, educa e entretém, "
            "transformando seguidores em clientes."
        ),
        llm=llm, verbose=False
    )

    # Agente 4: Focado em Email Marketing
    agente_email = Agent(
        role="Especialista em Email Marketing",
        goal=(
            "Criar 5 linhas de assunto (subject lines) magnéticas e um (1) "
            "curto e-mail de 'pitch' (apresentação) para {produto}."
        ),
        backstory=(
            "Sua especialidade é criar e-mails que são abertos, lidos e que "
            "geram cliques, usando o {tom_de_voz} correto para o {publico_alvo}."
        ),
        llm=llm, verbose=False
    )

    # ---------------------------
    # Tarefas de Marketing
    # ---------------------------

    # Tarefa 1: Slogans e CTAs (Executa primeiro)
    t_branding = Task(
        description=(
            "SLOGANS E CTAS\n"
            "Gere 5 slogans curtos e 5 CTAs (Calls-to-Action) para o {produto}, "
            "focando nos {beneficios} e no {publico_alvo}. "
            "Use o tom de voz: {tom_de_voz}. "
            "Formate em Markdown com títulos '## Slogans' e '## CTAs'."
        ),
        agent=agente_branding,
        expected_output="Duas listas em Markdown: 5 slogans e 5 CTAs."
    )

    # Tarefa 2: Anúncios (Usa o contexto de branding)
    t_anuncios = Task(
        description=(
            "ANÚNCIOS (PPC)\n"
            "Crie 2 variações de anúncios para Google Ads (2 Títulos, 1 Descrição curta) "
            "e 1 variação para Facebook/Instagram (1 Texto principal, 1 Título). "
            "Use os slogans e CTAs do contexto para se inspirar. "
            "Foque nos {beneficios} para o {publico_alvo}."
        ),
        agent=agente_copywriter,
        expected_output="Texto formatado em Markdown com as 3 variações de anúncios.",
        context=[t_branding] # Depende dos slogans
    )

    # Tarefa 3: Posts Sociais
    t_posts = Task(
        description=(
            "IDEIAS DE POSTS (MÍDIAS SOCIAIS)\n"
            "Liste 3 ideias de posts para {produto}. "
            "Para cada ideia, inclua: **Gancho (Hook)** (1 frase), **Descrição** (2-3 frases), **Hashtags** (3-5)."
        ),
        agent=agente_social,
        expected_output="Lista numerada (1-3) em Markdown com as ideias de posts."
    )

    # Tarefa 4: Conteúdo de Email
    t_email = Task(
        description=(
            "CONTEÚDO DE EMAIL\n"
            "1. Crie uma lista de 5 linhas de assunto (subjects) curtas e persuasivas. "
            "2. Escreva um (1) parágrafo curto (máx. 60 palavras) para um email de "
            "apresentação do {produto}. "
            "Formate em Markdown."
        ),
        agent=agente_email,
        expected_output="Markdown com a lista de subjects e o parágrafo do email."
    )

    # ---------------------------
    # Orquestração (Crew)
    # ---------------------------
    # Definindo a equipe e a ordem das tarefas
    agents = [agente_branding, agente_copywriter, agente_social, agente_email]
    tasks = [t_branding, t_anuncios, t_posts, t_email]

    crew = Crew(
        agents=agents,
        tasks=tasks,
        process=Process.sequential, # Tarefas executam em ordem
    )

    with st.spinner("Gerando conteúdo de marketing... 🚀"):
        crew.kickoff(inputs={
            "produto": produto,
            "publico_alvo": publico_alvo,
            "beneficios": beneficios,
            "tom_de_voz": tom_de_voz,
        })

    # ---------------------------
    # Exibição dos Resultados (em Abas)
    # ---------------------------
    
    # Lógica de extração de resultados (mantida igual à sua)
    branding_out = getattr(t_branding, "output", None) or getattr(t_branding, "result", "") or ""
    anuncios_out = getattr(t_anuncios, "output", None) or getattr(t_anuncios, "result", "") or ""
    posts_out = getattr(t_posts, "output", None) or getattr(t_posts, "result", "") or ""
    email_out = getattr(t_email, "output", None) or getattr(t_email, "result", "") or ""

    # Abas para cada tipo de conteúdo
    aba_branding, aba_anuncios, aba_posts, aba_email = st.tabs(
        ["Slogans & CTAs", "Anúncios (PPC)", "Posts Sociais", "Email"]
    )

    with aba_branding:
        st.markdown(branding_out)
    with aba_anuncios:
        st.markdown(anuncios_out)
    with aba_posts:
        st.markdown(posts_out)
    with aba_email:
        st.markdown(email_out)