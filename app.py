import streamlit as st
import openai
import time

# Configura tu API Key y Assistant ID
openai.api_key = st.secrets["OPENAI_API_KEY"]
ASSISTANT_ID = st.secrets["ASSISTANT_ID"]

# Funciones para interactuar con el Asistente


def crear_thread():
    response = openai.beta.threads.create()
    return response.id


def agregar_mensaje(thread_id, user_input):
    openai.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=user_input
    )


def ejecutar_asistente(thread_id):
    run = openai.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=ASSISTANT_ID,
        instructions="Responde únicamente basándote en los documentos proporcionados."
    )
    return run.id


def esperar_respuesta(thread_id, run_id):
    while True:
        run = openai.beta.threads.runs.retrieve(
            thread_id=thread_id, run_id=run_id)
        if run.status == "completed":
            messages = openai.beta.threads.messages.list(thread_id=thread_id)
            return messages.data[0].content[0].text.value
        elif run.status in ["requires_action", "expired", "failed", "cancelled"]:
            return "Error al procesar la respuesta."
        time.sleep(1)


# App de Streamlit
st.set_page_config(
    page_title="Asistente Financiero Corporativo", page_icon="📈")

st.title("📈 Asistente Financiero Corporativo")
st.caption(
    "Consulta información financiera basada exclusivamente en los documentos analizados.")

if "thread_id" not in st.session_state:
    st.session_state.thread_id = crear_thread()

# Formulario de input
with st.form("form_pregunta"):
    user_input = st.text_input(
        "¿Qué deseas preguntar?", placeholder="Ej: ¿Cómo evolucionó el patrimonio neto de Repsol entre 2018 y 2019?")
    submit_button = st.form_submit_button(label="Enviar")

if submit_button and user_input:
    with st.spinner("Buscando respuesta..."):
        agregar_mensaje(st.session_state.thread_id, user_input)
        run_id = ejecutar_asistente(st.session_state.thread_id)
        respuesta = esperar_respuesta(st.session_state.thread_id, run_id)
        st.success("Respuesta recibida:")
        st.write(respuesta)
    user_input = ""  # Limpiar el valor del cuadro de texto
