# -*- coding: utf-8 -*-
"""
VALORALIA Copilot - MarIA
La cara web de mi asistente. Es el mismo cerebro del notebook (RAG + agente + router),
metido en una interfaz de Streamlit con la que se puede hablar pinchando.

Las tasaciones orientativas usan el precio mediano REAL por metro cuadrado de mi dataset
de Pisos.com (no son valores inventados). La valoración exacta la da el modelo VALORALIA
completo, que además analiza las fotos del inmueble.

Para arrancarla:
    1) pip install -r requirements.txt
    2) Pongo mi clave de Gemini (barra lateral o st.secrets como GOOGLE_API_KEY)
    3) streamlit run app.py
"""

import os
import unicodedata
import streamlit as st

st.set_page_config(page_title="VALORALIA Copilot · MarIA", page_icon="🏠", layout="centered")

st.markdown(
    """
    <style>
      :root { --navy:#0A1628; --rojo:#C53030; --rosa:#D4537E; --gris:#4A5568; }
      .stApp { background: #FBF8F5; }
      h1, h2, h3 { font-family: Georgia, 'Times New Roman', serif; color: var(--navy); }
      .cabecera { background: var(--navy); color: #fff; padding: 22px 26px; border-radius: 12px; margin-bottom: 18px; }
      .cabecera .marca { font-family: Georgia, serif; font-size: 30px; font-weight: 700; }
      .cabecera .sub { color: #F4C0D1; font-style: italic; font-size: 16px; margin-top: 2px; }
      .ruta { display:inline-block; font-size: 12px; letter-spacing:.06em; text-transform:uppercase;
              font-weight:700; padding: 2px 10px; border-radius: 99px; margin-bottom: 6px; }
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
        "¿Cuánto valdría un piso de 80 m² con ascensor en Chamberí?",
        "Compárame Salamanca y Carabanchel en precio del metro cuadrado.",
        "¿Qué es un AVM?",
        "Quiero agendar una visita en Getafe.",
    ]

# ----------------------------------------------------------------------------
# Precio mediano REAL por metro cuadrado (mediana de mi dataset de Pisos.com).
# Datos extraídos de pisos_procesados_salvados.csv del TFM. Cubren todo Madrid:
# los distritos de la ciudad y los municipios del área metropolitana.
# ----------------------------------------------------------------------------
_DATOS_ZONAS = {
    "Salamanca": (12037, "Salamanca"),
    "Retiro": (9925, "Retiro"),
    "Chamberi": (9295, "Chamberí"),
    "Chamartin": (8200, "Chamartín"),
    "Centro": (8060, "Centro"),
    "Moncloa": (6313, "Moncloa-Aravaca"),
    "Tetuan": (5879, "Tetuán"),
    "Fuencarral": (5233, "Fuencarral-El Pardo"),
    "Ciudad_Lineal": (4943, "Ciudad Lineal"),
    "Pozuelo": (4842, "Pozuelo de Alarcón"),
    "Majadahonda": (4608, "Majadahonda"),
    "Moratalaz": (4545, "Moratalaz"),
    "San_Blas": (4184, "San Blas-Canillejas"),
    "Boadilla": (3939, "Boadilla del Monte"),
    "Alcobendas": (3936, "Alcobendas"),
    "Villa_Vallecas": (3832, "Villa de Vallecas"),
    "Las_Rozas": (3814, "Las Rozas"),
    "Vicalvaro": (3760, "Vicálvaro"),
    "Latina": (3750, "Latina"),
    "SS_Reyes": (3739, "San Sebastián de los Reyes"),
    "Usera": (3607, "Usera"),
    "Carabanchel": (3500, "Carabanchel"),
    "Villaviciosa_Odon": (3370, "Villaviciosa de Odón"),
    "Colmenar_Viejo": (3358, "Colmenar Viejo"),
    "Tres_Cantos": (3210, "Tres Cantos"),
    "Puente_Vallecas": (3186, "Puente de Vallecas"),
    "Getafe": (3133, "Getafe"),
    "Alcorcon": (3080, "Alcorcón"),
    "Leganes": (3029, "Leganés"),
    "Coslada": (2942, "Coslada"),
    "Torrejon": (2934, "Torrejón de Ardoz"),
    "Rivas": (2852, "Rivas-Vaciamadrid"),
    "Pinto": (2848, "Pinto"),
    "Fuenlabrada": (2824, "Fuenlabrada"),
    "Villaverde": (2814, "Villaverde"),
    "Alcala_Henares": (2811, "Alcalá de Henares"),
    "Mostoles": (2809, "Móstoles"),
    "Parla": (2282, "Parla"),
    "Arganda": (1973, "Arganda del Rey"),
}


def _norm(s):
    """Normaliza una zona: minúsculas, sin tildes, sin palabras de enlace ni signos."""
    s = (s or "").lower().strip()
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    s = s.replace("_", " ").replace("-", " ").replace(".", " ").replace(",", " ")
    stop = {"de", "del", "la", "los", "las", "el", "y"}
    return "".join(t for t in s.split() if t not in stop)


PRECIO_M2 = {}
NOMBRE_ZONA = {}
for _raw, (_med, _nice) in _DATOS_ZONAS.items():
    _k = _norm(_raw)
    PRECIO_M2[_k] = _med
    NOMBRE_ZONA[_k] = _nice

# Alias para nombres que en el dataset van abreviados.
ALIAS = {"sansebastianreyes": _norm("SS_Reyes"), "sanse": _norm("SS_Reyes")}


def _buscar_zona(entrada):
    n = _norm(entrada)
    if not n:
        return None
    if n in PRECIO_M2:
        return n
    if n in ALIAS:
        return ALIAS[n]
    for k in PRECIO_M2:
        if n.startswith(k) or k.startswith(n) or (len(k) >= 5 and k in n) or (len(n) >= 5 and n in k):
            return k
    return None


def _eur(x):
    return f"{x:,.0f}".replace(",", ".")


RUTA_MODELO = "/content/drive/MyDrive/TFM_VALORALIA_3/03_Models/valoralia_production_B.pkl"

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
        "viviendas en Madrid, abarcando los 21 distritos de la ciudad y los municipios de su área "
        "metropolitana. El modelo es híbrido: combina variables tabulares de la vivienda "
        "(superficie, habitaciones, baños, planta, ascensor, terraza, garaje, estado de reforma) "
        "con componentes visuales extraídas de las fotografías del anuncio mediante la red "
        "ResNet50. El algoritmo final es un modelo de gradient boosting que alcanza un coeficiente "
        "de determinación logarítmico en torno a 0,91 y un error porcentual medio cercano al 20 por "
        "ciento. Los datos proceden de anuncios reales de Pisos.com. El resultado se ofrece como "
        "una estimación central acompañada de un intervalo.")},
    {"titulo": "Zonas que cubre VALORALIA", "contenido": (
        "VALORALIA cubre el conjunto de Madrid. Por un lado, los distritos de la ciudad, desde los "
        "más caros (Salamanca, Retiro, Chamberí, Chamartín, Centro) hasta los más asequibles "
        "(Villaverde, Usera, Puente de Vallecas, Carabanchel, Latina). Por otro, numerosos "
        "municipios del área metropolitana, tanto del sur (Getafe, Leganés, Alcorcón, Móstoles, "
        "Fuenlabrada, Parla, Pinto) como del norte y oeste (Pozuelo de Alarcón, Las Rozas, "
        "Majadahonda, Boadilla del Monte, Alcobendas, Tres Cantos) y del este (Alcalá de Henares, "
        "Torrejón de Ardoz, Coslada, Rivas-Vaciamadrid). El modelo se entrenó con anuncios reales "
        "de Pisos.com en todas estas zonas, lo que abarca un mercado muy diverso en precios.")},
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

    modelo_valoralia = None
    try:
        import joblib
        modelo_valoralia = joblib.load(RUTA_MODELO)
    except Exception:
        modelo_valoralia = None

    @tool
    def estimar_precio_vivienda(zona: str, superficie_m2: float, habitaciones: int = 3,
                                banos: int = 1, ascensor: bool = True) -> str:
        """Estima de forma orientativa el precio de venta de una vivienda en Madrid: los distritos
        de la ciudad (Chamberí, Centro, Salamanca, Retiro, Carabanchel, Usera...) o los municipios
        del área metropolitana (Getafe, Pozuelo, Las Rozas, Alcalá de Henares...). Recibe la zona y
        la superficie en metros cuadrados."""
        k = _buscar_zona(zona)
        if k is None:
            return (f"No tengo el dato de '{zona}' en mi base de zonas. VALORALIA cubre los "
                    f"distritos de Madrid y su área metropolitana; prueba con otra zona "
                    f"(por ejemplo Chamberí, Centro, Getafe o Pozuelo).")
        eur_m2 = PRECIO_M2[k]
        central = eur_m2 * superficie_m2
        margen = 0.20  # error porcentual medio del modelo (MAPE en torno al 20 %)
        bajo, alto = central * (1 - margen), central * (1 + margen)
        return (
            f"Estimación orientativa para {NOMBRE_ZONA[k]} ({superficie_m2:.0f} m²):\n"
            f"- Precio mediano real de la zona: {_eur(eur_m2)} EUR/m² (mediana de mi dataset de Pisos.com).\n"
            f"- Valoración central orientativa: {_eur(central)} EUR.\n"
            f"- Intervalo orientativo: entre {_eur(bajo)} y {_eur(alto)} EUR.\n"
            f"Es una estimación por metro cuadrado a partir de mis datos reales. La valoración exacta "
            f"la da el modelo VALORALIA completo, que además tiene en cuenta el ascensor, el estado de "
            f"reforma y las fotos del inmueble."
        )

    @tool
    def comparar_zonas(zona_a: str, zona_b: str) -> str:
        """Compara el precio mediano del metro cuadrado entre dos zonas de Madrid (distritos de la
        ciudad o municipios del área metropolitana)."""
        ka, kb = _buscar_zona(zona_a), _buscar_zona(zona_b)
        if ka is None or kb is None:
            falla = zona_a if ka is None else zona_b
            return f"No tengo el dato de '{falla}' en mi base de zonas de Madrid."
        pa, pb = PRECIO_M2[ka], PRECIO_M2[kb]
        cara = NOMBRE_ZONA[ka] if pa > pb else NOMBRE_ZONA[kb]
        return (f"{NOMBRE_ZONA[ka]}: {_eur(pa)} EUR/m². {NOMBRE_ZONA[kb]}: {_eur(pb)} EUR/m². "
                f"{cara} es más cara, con una diferencia de {_eur(abs(pa - pb))} EUR/m². "
                f"(Mediana de precios reales de mi dataset de Pisos.com.)")

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
        "de Madrid (los distritos de la ciudad y los municipios de su área metropolitana). Razonas "
        "paso a paso: piensas qué necesita el usuario, decides si hace falta una herramienta, la "
        "usas, observas el resultado y construyes la respuesta. Si la pregunta es de cálculo o "
        "tasación, usa estimar_precio_vivienda. Si pide comparar zonas, usa comparar_zonas. Si es "
        "informativa (impuestos, normativa, conceptos), usa buscar_documentacion y no respondas de "
        "memoria temas delicados. Si quiere una visita, usa solicitar_visita y recuerda que queda "
        "pendiente de confirmación humana. Responde en español de España, claro y cercano, y si no "
        "puedes ayudar, dilo con honestidad.")
    ejecutor = create_react_agent(llm, herramientas, prompt=system_prompt)

    def _texto_limpio(content):
        # Las versiones nuevas de Gemini devuelven el contenido como lista de bloques.
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            partes = []
            for bloque in content:
                if isinstance(bloque, dict):
                    partes.append(bloque.get("text", ""))
                else:
                    partes.append(str(bloque))
            return "".join(partes).strip()
        return str(content)

    def clasificar_pregunta(pregunta: str) -> str:
        instruccion = (
            "Clasifica la siguiente pregunta de un usuario de una inmobiliaria en una sola palabra:\n"
            "- ACCION si pide tasar, calcular un precio, comparar zonas o agendar una visita.\n"
            "- INFORMACION si pregunta por conceptos, impuestos, normativa, definiciones o datos.\n"
            f"Pregunta: {pregunta}\n"
            "Responde solo con ACCION o INFORMACION, sin nada más.")
        etiqueta = _texto_limpio(llm.invoke(instruccion).content).strip().upper()
        return "ACCION" if "ACCION" in etiqueta else "INFORMACION"

    def responder(pregunta: str):
        ruta = clasificar_pregunta(pregunta)
        if ruta == "ACCION":
            salida = ejecutor.invoke({"messages": [("human", pregunta)]})
            return ruta, _texto_limpio(salida["messages"][-1].content)
        return ruta, _texto_limpio(cadena_rag.invoke(pregunta))

    return responder, (modelo_valoralia is not None)


if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "ruta": None,
         "content": "Hola, soy MarIA. Puedo resolver dudas del mercado inmobiliario y dar una "
                    "estimación orientativa de viviendas en Madrid (los distritos de la ciudad y "
                    "su área metropolitana). ¿En qué te ayudo?"}
    ]

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


with st.sidebar:
    for ej in ejemplos:
        if st.button(ej, use_container_width=True):
            lanzar(ej)
            st.rerun()

pregunta = st.chat_input("Escribe tu pregunta para MarIA...")
if pregunta:
    lanzar(pregunta)
    st.rerun()
