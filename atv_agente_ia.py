import os
import streamlit as st 
from crewai import Agent, Task, Crew, Process, LLM

# ==============================================
# APP: Learn Korean 🇰🇷
# ==============================================

st.header(" 🐅 Learn Korean with AI Agents 🫰")
st.write("Enter a topic (vocabulary, grammar, expressions, etc.) and generate learning material:")

topic = st.text_input("Learning topic: ", placeholder="e.g., Greetings, Numbers, Basic Verbs")
goal = st.text_input("Learning goal: ", placeholder="e.g., Learn common Korean greetings")
execute = st.button("Generate Study Material")

api_key = 'API_KEY'  # Replace with your actual API key

if execute:
    # ==============================================
    # LLM CONFIGURATION
    # ==============================================
    llm = LLM(
        model="groq/llama-3.3-70b-versatile",
        api_key=api_key,
        temperature=0.4
    )

    # ==============================================
    # AGENTS
    # ==============================================

    agent_explainer = Agent(
    role="Korean language teacher and cultural guide.",
    goal=(
        "Clearly explain the topic {topic} in English, aligned with the goal {goal}. "
        "Always include Korean words or phrases in **Hangul**, followed by **romanization in parentheses**, "
        "and an **English translation**. Never omit Hangul.\n\n"
        "After your explanation, include a short **Commentary** section where you: \n"
        "- Add cultural notes or usage tips (e.g., when or how native speakers actually use the expressions).\n"
        "- Mention any common mistakes learners make.\n"
        "- Suggest a simple memory trick or pronunciation tip.\n\n"
        "Example format:\n"
        "### Vocabulary\n"
        "- 하나 (hana): one\n"
        "- 둘 (dul): two\n\n"
        "### Commentary\n"
        'In Korean, numbers often come before measure words, like "개" (gae) for counting items. '
        "So '두 개' (du gae) means 'two things'. Practice these with rhythm to remember them easily!"
    ),
    backstory="You are a friendly Korean teacher who also gives cultural context, tips, and personal-style commentary to make learning fun and memorable.",
    llm=llm, verbose=False
    )

    agent_examples = Agent(
    role="Creator of Korean examples and mini-dialogues.",
    goal=(
        "Create **10 short Korean sentences or mini-dialogues** about {topic}. "
        "Each must include:\n"
        "- Korean sentence written in Hangul\n"
        "- Romanization in parentheses directly after the Hangul\n"
        "- English translation below it\n\n"
        "Make sure they vary in tone and situation (e.g., daily conversation, polite forms, casual phrases, questions, short exchanges).\n"
        "Example:\n"
        "안녕하세요! (annyeonghaseyo!) — Hello!\n"
        "저는 학생이에요. (jeoneun haksaeng-ieyo.) — I am a student.\n"
        "몇 살이에요? (myeot sal-ieyo?) — How old are you?"
    ),
    backstory="You always produce diverse, real-world Korean sentences using Hangul, romanization, and translation.",
    llm=llm, verbose=False
    )

    # ==============================================
    # TASKS
    # ==============================================

    t_explanation = Task(
    description=(
        "Write a structured and beginner-friendly explanation about {topic} related to {goal}. "
        "Include:\n"
        "- Introduction and context (2–3 sentences)\n"
        "- Vocabulary list or grammar explanation (with Hangul, romanization, and translation)\n"
        "- Example usage\n"
        "- A final section titled '### Commentary' with cultural notes, tips, and insights.\n\n"
        "Format in Markdown for clarity."
    ),
    agent=agent_explainer,
    expected_output="Markdown-formatted text with an Introduction, Vocabulary/Explanation, and Commentary sections."
    )

    t_examples = Task(
        description=(
            "Generate 20 short Korean sentences or mini-dialogues related to {topic}. "
            "Each should show: \n"
            "- Korean (Hangul)\n"
            "- Romanization\n"
            "- English translation"
        ),
        agent=agent_examples,
        expected_output="A numbered list (1–20) in Markdown with full examples and translations."
    )

    # ==============================================
    # CREW SETUP
    # ==============================================
    agents = [agent_explainer, agent_examples]
    tasks = [t_explanation, t_examples]

    crew = Crew(
        agents=agents,
        tasks=tasks,
        process=Process.sequential
    )

    # Run the crew
    crew.kickoff(inputs={
        "topic": topic,
        "goal": goal or "not specified"
    })

    # ==============================================
    # DISPLAY RESULTS
    # ==============================================
    explanation_out = getattr(t_explanation, "output", None) or getattr(t_explanation, "result", "") or ""
    examples_out = getattr(t_examples, "output", None) or getattr(t_examples, "result", "") or ""

    # Tabs for output
    tab_explanation, tab_examples = st.tabs(
        ["📖 Explanation", "💬 Sentences & Dialogues"]
    )

    with tab_explanation:
        st.markdown(explanation_out)
    with tab_examples:
        st.markdown(examples_out)