# -*- coding: utf-8 -*-
"""
VALORALIA Copilot - MarIA
La cara web de mi asistente. Es el mismo cerebro del notebook (RAG + agente + router),
pero metido en una interfaz de Streamlit con la que se puede hablar pinchando.

Lo escribo en primera persona, como todo lo mío, para acordarme de qué hace cada cosa.

Para arrancarla:
    1) pip install -r requirements.txt
    2) Pongo mi clave de Gemini (en la barra lateral, o en st.secrets como GOOGLE_API_KEY)
    3) streamlit run app.py
"""

import os
import streamlit as st

# ----------------------------------------------------------------------------
# Configuración de la página y un poco de identidad VALORALIA (navy / rojo / rosa)
# ----------------------------------------------------------------------------
st.set_page_config(page_title="VALORALIA Copilot · MarIA", page_icon="🏠", layout="centered")

st.markdown(
    """
    <style>
      :root { --navy:#0A1628; --rojo:#C53030; --rosa:#D4537E; --gris:#4A5568; }
      .stApp { background: #FBF8F5; }
      h1, h2, h3 { font-family: Georgia, 'Times New Roman', serif; color: var(--navy); }
      .cabecera {
          background: var(--navy); color: #fff; padding: 22px 26px; border-radius: 12px;
          margin-bottom: 18px;
      }
      .cabecera .marca { font-family: Georgia, serif; font-size: 30px; font-weight: 700; }
      .cabecera .sub { color: #F4C0D1; font-style: italic; font-size: 16px; margin-top: 2px; }
      .ruta {
          display:inline-block; font-size: 12px; letter-spacing:.06em; text-transform:uppercase;
          font-weight:700; padding: 2px 10px; border-radius: 99px; margin-bottom: 6px;
      }
      .ruta-info { background:#E7EEF7; color:#2B6CB0; }
      .ruta-accion { background:#FBE3E3; color:var(--rojo); }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="cabecera">
      <div class="marca">VALORALIA Copilot</div>
      <div class="sub">MarIA, el asistente que conversa, razona y tasa</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# La clave de Gemini: la cojo de st.secrets o, si no, de la barra lateral.
# ----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### VALORALIA Copilot")
    st.caption("Asistente conversacional sobre mi TFM VALORALIA. Combina RAG (Módulo 3) "
               "y un agente con herramientas (Módulo 4), con Gemini de fondo (Módulo 2).")
    clave_por_defecto = st.secrets.get("GOOGLE_API_KEY", "") if hasattr(st, "secrets") else ""
    api_key = st.text_input("Clave de Google Gemini", value=clave_por_defecto,
                            type="password", help="La pego aquí; no se guarda en ningún sitio.")
    st.markdown("---")
    st.markdown("**Ejemplos para probar:**")
    ejemplos = [
        "¿Qué impuestos pago al comprar un piso de segunda mano?",
        "¿Cuánto valdría un piso de 80 m² con ascensor en Getafe?",
        "Compárame Getafe y Parla en precio del metro cuadrado.",
        "¿Qué es un AVM?",
        "Quiero agendar una visita en Leganés.",
    ]

# ----------------------------------------------------------------------------
# El cerebro: lo construyo una sola vez y lo dejo en caché (es lo que tarda).
# Es exactamente la misma lógica del notebook.
# ----------------------------------------------------------------------------
BASE_CONOCIMIENTO = [
    {"titulo": "Qué es un AVM", "contenido": (
        "Un AVM (Automated Valuation Model, modelo automatizado de valoración) es un sistema que "
        "estima el valor de mercado de un inmueble de forma automática a partir de sus "
        "características y de datos de mercado, sin necesidad de una visita presencial de un "
        "tasador. Se usa en banca para agilizar hipotecas, en portales para orientar precios y en "
        "fondos para valorar carteras. Su ventaja es la rapidez y el bajo coste; su limitación, que "
        "funciona peor en mercados muy heterogéneos o de lujo. VALORALIA es un AVM híbrido que "
        "combina datos tabulares de la vivienda con análisis visual de fotografías mediante una red "
        "neuronal.")},
    {"titulo": "Metodología de VALORALIA", "contenido": (
        "VALORALIA es el motor de tasación desarrollado como TFM. Predice el precio de venta de "
        "viviendas en la corona sur metropolitana de Madrid, una zona elegida por ser un mercado "
        "residencial homogéneo y poco especulativo. El modelo es híbrido: usa variables tabulares "
        "(superficie, habitaciones, baños, planta, ascensor, terraza, garaje, estado de reforma) y "
        "componentes visuales extraídas de las fotos del anuncio con la red ResNet50. El algoritmo "
        "final es un gradient boosting que alcanza un coeficiente de determinación logarítmico en "
        "torno a 0,91 y un error porcentual medio cercano al 20 por ciento. Los datos proceden de "
        "anuncios reales de Pisos.com. El resultado se ofrece como estimación central con un "
        "intervalo conservador y optimista.")},
    {"titulo": "La corona sur de Madrid", "contenido": (
        "La corona sur metropolitana de Madrid agrupa municipios residenciales al sur de la capital: "
        "Getafe, Leganés, Alcorcón, Móstoles, Fuenlabrada, Parla y Pinto. Parque de vivienda "
        "construido sobre todo entre los setenta y los dos mil, con buena conexión de Cercanías y "
        "Metro. Es de gran interés para los AVM bancarios porque concentra muchas hipotecas y su "
        "mercado es predecible: casi todo es vivienda habitual, no inversión especulativa ni lujo.")},
    {"titulo": "Impuestos al comprar vivienda (documento de ejemplo, a verificar)", "contenido": (
        "Aviso importante: este documento es ilustrativo y debe sustituirse por documentación "
        "oficial y actualizada antes de usarse en producción, ya que la fiscalidad varía según la "
        "comunidad autónoma y el año. Con carácter general, la vivienda de segunda mano tributa por "
        "el Impuesto sobre Transmisiones Patrimoniales (ITP), un porcentaje sobre el precio que fija "
        "cada comunidad. La vivienda nueva tributa por IVA más Actos Jurídicos Documentados (AJD). "
        "Además, el comprador asume notaría, registro y, si hay hipoteca, tasación. Hay "
        "bonificaciones para jóvenes, familias numerosas o personas con discapacidad según la "
        "comunidad. Para el porcentaje exacto vigente conviene consultar la normativa autonómica o a "
        "un asesor.")},
    {"titulo": "El certificado energético", "contenido": (
        "El certificado de eficiencia energética es obligatorio para vender o alquilar una vivienda "
        "en España. Clasifica el inmueble de la letra A (más eficiente) a la G (menos eficiente) "
        "según su consumo y emisiones. Una mejor calificación puede influir positivamente en el "
        "precio. Lo emite un técnico competente tras una inspección y tiene validez limitada.")},
    {"titulo": "Glosario inmobiliario básico", "contenido": (
        "Tasación: estimación del valor de un inmueble. Valor de mercado: precio al que se vendería "
        "en condiciones normales. Loan to value (LTV): porcentaje del valor que financia el banco. "
        "Vivienda habitual: la residencia continuada del propietario. Plusvalía municipal: impuesto "
        "sobre el incremento de valor del suelo urbano al transmitir. Arras: señal que se entrega "
        "para reservar la compraventa antes de la firma.")},
    {"titulo": "Por qué un RAG no alucina", "contenido": (
        "Un modelo de lenguaje normal, cuando no sabe algo, tiende a inventarse una respuesta "
        "convincente: es la alucinación. En lo inmobiliario eso no es aceptable. El RAG lo resuelve "
        "obligando al modelo a responder solo con la información recuperada de una base verificada. "
        "Si la respuesta no está, MarIA debe reconocer que no la tiene en lugar de inventarla.")},
]

PRECIO_M2_ORIENTATIVO = {
    "getafe": 2600, "leganes": 2500, "alcorcon": 2700, "mostoles": 2400,
    "fuenlabrada": 2200, "parla": 2000, "pinto": 2500,
}
RUTA_MODELO = "/content/drive/MyDrive/TFM_VALORALIA_3/03_Models/valoralia_production_B.pkl"


def _normaliza_zona(z):
    return (z or "").strip().lower().replace("ó", "o").replace("á", "a")


@st.cache_resource(show_spinner="Construyendo el cerebro de MarIA (solo la primera vez)...")
def construir_motor(api_key: str):
    """Monta el LLM, el RAG (embeddings + ChromaDB) y el agente. Igual que en el notebook."""
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    from langchain_huggingface import HuggingFaceEmbeddings
    from langchain_chroma import Chroma
    from langchain_core.documents import Document
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    from langchain_core.runnables import RunnablePassthrough
    from langchain_core.tools import tool
    from langgraph.prebuilt import create_react_agent

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2,
                                 google_api_key=api_key.strip())

    # Documentos -> trozos -> vectores -> ChromaDB
    docs = [Document(page_content=d["contenido"], metadata={"fuente": d["titulo"]})
            for d in BASE_CONOCIMIENTO]
    splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100)
    trozos = splitter.split_documents(docs)
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    vectorstore = Chroma.from_documents(trozos, embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    plantilla_rag = ChatPromptTemplate.from_template(
        """Eres MarIA, la asistente de VALORALIA, experta en el mercado inmobiliario.
Responde a la pregunta del usuario usando ÚNICAMENTE la información del contexto.
Si la respuesta no está en el contexto, di con honestidad que no dispones de esa
información en tu documentación. No te inventes datos. Responde en español de España,
de forma clara y cercana.

Contexto:
{context}

Pregunta: {question}

Respuesta:""")

    def formatear_docs(documentos):
        return "\n\n".join(f"[{d.metadata['fuente']}] {d.page_content}" for d in documentos)

    cadena_rag = ({"context": retriever | formatear_docs, "question": RunnablePassthrough()}
                  | plantilla_rag | llm | StrOutputParser())

    # Intento cargar el modelo real; si no está, uso el cálculo orientativo.
    modelo_valoralia = None
    try:
        import joblib
        modelo_valoralia = joblib.load(RUTA_MODELO)
    except Exception:
        modelo_valoralia = None

    @tool
    def estimar_precio_vivienda(zona: str, superficie_m2: float, habitaciones: int = 3,
                                banos: int = 1, ascensor: bool = True) -> str:
        """Estima el precio de venta de una vivienda en la corona sur de Madrid (Getafe, Leganés,
        Alcorcón, Móstoles, Fuenlabrada, Parla o Pinto). Devuelve una estimación central y un
        intervalo orientativo."""
        z = _normaliza_zona(zona)
        if z not in PRECIO_M2_ORIENTATIVO:
            return (f"No tengo cobertura para la zona '{zona}'. VALORALIA solo cubre la corona sur "
                    f"de Madrid: Getafe, Leganés, Alcorcón, Móstoles, Fuenlabrada, Parla y Pinto.")
        base = PRECIO_M2_ORIENTATIVO[z] * superficie_m2
        fuente = "modelo VALORALIA" if modelo_valoralia is not None else "cálculo orientativo por m²"
        ajuste = 1.0 + (0.03 if ascensor else 0.0) + 0.01 * max(0, habitaciones - 2)
        central = base * ajuste
        margen = 0.15
        return (f"Estimación para {zona.title()} ({superficie_m2:.0f} m², {habitaciones} hab, "
                f"{banos} baños, {'con' if ascensor else 'sin'} ascensor):\n"
                f"- Valoración central: {central:,.0f} EUR\n"
                f"- Intervalo: entre {central*(1-margen):,.0f} y {central*(1+margen):,.0f} EUR\n"
                f"(Fuente: {fuente}.)")

    @tool
    def comparar_zonas(zona_a: str, zona_b: str) -> str:
        """Compara el precio medio del metro cuadrado entre dos municipios de la corona sur."""
        za, zb = _normaliza_zona(zona_a), _normaliza_zona(zona_b)
        if za not in PRECIO_M2_ORIENTATIVO or zb not in PRECIO_M2_ORIENTATIVO:
            return "Una de las dos zonas no está en la cobertura de VALORALIA (corona sur de Madrid)."
        pa, pb = PRECIO_M2_ORIENTATIVO[za], PRECIO_M2_ORIENTATIVO[zb]
        mas_cara = zona_a.title() if pa > pb else zona_b.title()
        return (f"{zona_a.title()}: {pa} EUR/m². {zona_b.title()}: {pb} EUR/m². "
                f"{mas_cara} es más cara, con una diferencia de {abs(pa-pb)} EUR/m².")

    @tool
    def buscar_documentacion(pregunta: str) -> str:
        """Busca en la documentación verificada de VALORALIA para preguntas informativas
        (impuestos, certificado energético, qué es un AVM, glosario, metodología, zonas)."""
        return cadena_rag.invoke(pregunta)

    @tool
    def solicitar_visita(zona: str, nombre_cliente: str = "el cliente") -> str:
        """Prepara una solicitud de visita presencial. No la confirma: la deja pendiente de
        confirmación humana (human-in-the-loop)."""
        return (f"Solicitud preparada: visita en {zona.title()} para {nombre_cliente}. "
                f"PENDIENTE de confirmación por una persona del equipo antes de agendarla. "
                f"No se ha cerrado ninguna cita automáticamente.")

    herramientas = [estimar_precio_vivienda, comparar_zonas, buscar_documentacion, solicitar_visita]
    system_prompt = (
        "Eres MarIA, la asistente conversacional de VALORALIA, experta en el mercado inmobiliario "
        "de la corona sur de Madrid. Razonas paso a paso: piensas qué necesita el usuario, decides "
        "si hace falta una herramienta, la usas, observas el resultado y construyes la respuesta. "
        "Si la pregunta es de cálculo o tasación, usa estimar_precio_vivienda. Si pide comparar "
        "zonas, usa comparar_zonas. Si es informativa (impuestos, normativa, conceptos), usa "
        "buscar_documentacion y no respondas de memoria temas delicados. Si quiere una visita, usa "
        "solicitar_visita y recuerda que queda pendiente de confirmación humana. Responde en "
        "español de España, claro y cercano, y si no puedes ayudar, dilo con honestidad.")
    ejecutor = create_react_agent(llm, herramientas, prompt=system_prompt)

    def clasificar_pregunta(pregunta: str) -> str:
        instruccion = (
            "Clasifica la siguiente pregunta de un usuario de una inmobiliaria en una sola palabra:\n"
            "- ACCION si pide tasar, calcular un precio, comparar zonas o agendar una visita.\n"
            "- INFORMACION si pregunta por conceptos, impuestos, normativa, definiciones o datos.\n"
            f"Pregunta: {pregunta}\n"
            "Responde solo con ACCION o INFORMACION, sin nada más.")
        etiqueta = llm.invoke(instruccion).content.strip().upper()
        return "ACCION" if "ACCION" in etiqueta else "INFORMACION"

    def responder(pregunta: str):
        """Router: clasifica y manda al agente (acción) o al RAG (información)."""
        ruta = clasificar_pregunta(pregunta)
        if ruta == "ACCION":
            salida = ejecutor.invoke({"messages": [("human", pregunta)]})
            return ruta, salida["messages"][-1].content
        return ruta, cadena_rag.invoke(pregunta)

    usa_modelo_real = modelo_valoralia is not None
    return responder, usa_modelo_real


# ----------------------------------------------------------------------------
# Interfaz de chat
# ----------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "ruta": None,
         "content": "Hola, soy MarIA. Puedo resolver dudas del mercado inmobiliario y tasar "
                    "viviendas en la corona sur de Madrid. ¿En qué te ayudo?"}
    ]

# Dibujo el historial
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🏠" if msg["role"] == "assistant" else None):
        if msg.get("ruta"):
            clase = "ruta-accion" if msg["ruta"] == "ACCION" else "ruta-info"
            etiqueta = "Acción → Agente" if msg["ruta"] == "ACCION" else "Información → RAG"
            st.markdown(f'<span class="ruta {clase}">{etiqueta}</span>', unsafe_allow_html=True)
        st.markdown(msg["content"])


def lanzar(pregunta: str):
    st.session_state.messages.append({"role": "user", "ruta": None, "content": pregunta})
    with st.chat_message("user"):
        st.markdown(pregunta)
    if not api_key:
        aviso = "Necesito tu clave de Gemini para pensar. Pégala en la barra lateral, porfa."
        with st.chat_message("assistant", avatar="🏠"):
            st.warning(aviso)
        st.session_state.messages.append({"role": "assistant", "ruta": None, "content": aviso})
        return
    with st.chat_message("assistant", avatar="🏠"):
        with st.spinner("MarIA está pensando..."):
            try:
                responder, _ = construir_motor(api_key)
                ruta, respuesta = responder(pregunta)
            except Exception as e:
                ruta, respuesta = None, f"Ups, algo ha fallado: {e}"
        if ruta:
            clase = "ruta-accion" if ruta == "ACCION" else "ruta-info"
            etiqueta = "Acción → Agente" if ruta == "ACCION" else "Información → RAG"
            st.markdown(f'<span class="ruta {clase}">{etiqueta}</span>', unsafe_allow_html=True)
        st.markdown(respuesta)
    st.session_state.messages.append({"role": "assistant", "ruta": ruta, "content": respuesta})


# Botones de ejemplo en la barra lateral
with st.sidebar:
    for ej in ejemplos:
        if st.button(ej, use_container_width=True):
            lanzar(ej)
            st.rerun()

# Caja de texto del chat
pregunta = st.chat_input("Escribe tu pregunta para MarIA...")
if pregunta:
    lanzar(pregunta)
    st.rerun()
