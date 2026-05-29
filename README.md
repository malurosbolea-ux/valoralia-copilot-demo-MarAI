# VALORALIA Copilot (MarIA): Asistente conversacional con RAG y agentes

¡Hola! Soy María Luisa Ros Bolea, y esta memoria documenta **VALORALIA Copilot**, al que he llamado cariñosamente **MarIA**. Es un asistente conversacional que combina recuperación aumentada por generación (RAG) y un agente con herramientas, construido sobre **VALORALIA**, el motor de tasación inmobiliaria que desarrollé como Trabajo de Fin de Máster en el CEU San Pablo (Madrid).

## 🔗 Enlaces del proyecto

Para que puedas probar el sistema en vivo y ver cómo razona, aquí tienes los accesos directos:
* **Demo web interactiva (Streamlit):** [MarIA Streamlit](https://valoralia-copilot-demo-marai-nan6wokkfuzmbjcvpmmwl4.streamlit.app/)
* **Código fuente:** [Google Colab](https://colab.research.google.com/drive/1Cu0X1PYFW4Nnv-6URQETEeO0zkXwhNdQ?usp=sharing)
* **Motor original del TFM:** [VALORALIA en AWS](http://51.20.2.178/)
* **Repositorio:** [GitHub](https://github.com/malurosbolea-ux/valoralia-copilot-demo-MarAI)

## 💡 Introducción y motivación

Los modelos de lenguaje son muy capaces, pero cuando no conocen la respuesta tienden a inventarla con total seguridad (lo que conocemos como alucinación). En un dominio como el inmobiliario eso no es un detalle menor: una cifra equivocada sobre impuestos o sobre normativa tiene consecuencias reales. 

Por eso quería construir un asistente en el que se pudiera confiar al 100%. La técnica del RAG obliga al modelo a responder únicamente a partir de documentos verificados. Sobre esa base, he añadido un agente capaz de razonar y de ejecutar acciones a través de herramientas, una de las cuales es mi propio motor de tasación.

Dicho de otro modo: en mi TFM construí el "cerebro" que predice, y en esta práctica he construido el "cuerpo" que conversa, razona y decide cuándo usar ese cerebro.

## 🏗️ Arquitectura del sistema

El sistema parte de un componente sencillo pero decisivo, el **router**, que clasifica cada pregunta en dos caminos:

1. **Información (RAG):** Si la pregunta es informativa (impuestos, normativa, conceptos), la envía al RAG, que responde solo desde la documentación verificada.
2. **Acción (Agente):** Si la pregunta pide una acción (tasar, comparar zonas, agendar una visita), la envía al agente, que razona y ejecuta herramientas.

El RAG, además, está disponible como una herramienta más del agente, aplicando un patrón avanzado que se conoce como *RAG agéntico*. Todo el sistema utiliza **Gemini 2.5 Flash** por su excelente capacidad para *tool calling*, y **ChromaDB** como base de datos vectorial.

## 🛠️ Las herramientas del agente

Le he dado cuatro herramientas principales, cada una definida como una función de Python pura:
* `estimar_precio_vivienda`: Integra mi motor VALORALIA para tasar inmuebles.
* `comparar_zonas`: Devuelve la diferencia de precio por metro cuadrado entre dos municipios.
* `buscar_documentacion`: Envuelve el RAG completo para que el agente consulte la base de conocimiento cuando lo necesite.
* `solicitar_visita`: Aplica el patrón *human-in-the-loop*, preparando la solicitud comercial pero dejándola pendiente de confirmación humana.

## 📊 Evaluación (RAGAS + Juez propio)

Un RAG no se valida a ojo, se mide. He evaluado el sistema de dos formas independientes para asegurar resultados sólidos: con el framework oficial **RAGAS** y con un juez propio basado en LLM (*LLM-as-a-judge*).

| Métrica | Valor | Qué mide |
|---|---|---|
| **Faithfulness** (RAGAS) | 0.75 | Si la respuesta se apoya en el contexto recuperado y no inventa. |
| **Answer relevancy** (RAGAS) | 0.90 | Si la respuesta va al grano de lo que se pregunta. |
| **Context precision** (RAGAS) | 0.88 | De lo recuperado, qué proporción es relevante. |
| **Context recall** (RAGAS) | 1.00 | De lo relevante, qué proporción se recupera. |
| **Fidelidad** (Juez propio) | 0.93 | Mi propia medida de fidelidad con un LLM como juez. |
| **Relevancia** (Juez propio) | 1.00 | Mi propia medida de relevancia con un LLM como juez. |
| **Acierto del router** | 100% | Clasificación correcta entre información y acción. |

*Nota sobre la fidelidad:* El 0.75 en RAGAS es esperado y positivo. Algunas respuestas añaden matices de prudencia muy necesarios (como recomendar consultar a un asesor fiscal) que no aparecen literalmente en el documento base, lo que penaliza la métrica pero mejora el producto real.

## 🚀 Limitaciones y líneas futuras

Ser honesta con las limitaciones también forma parte de un trabajo excelente. La base de conocimiento está curada por mí (unas 11 páginas de contenido verificado), por lo que en producción habría que conectarla a documentación oficial. Además, la herramienta de tasación en la demo de Streamlit utiliza valores orientativos mientras no conecto el `.pkl` real de VALORALIA por peso de los archivos.

Como líneas futuras me planteo:
1. Conectar el modelo real de VALORALIA.
2. Ampliar la documentación con normativa autonómica.
3. Dotar a MarIA de memoria de conversación entre turnos.
4. Desplegar el asistente sobre la infraestructura de AWS donde ya vive el motor de tasación.

---
*Desarrollado con muchísimo mimo y en tonos pastel por **María Luisa Ros Bolea**.* *Máster en Big Data e Inteligencia Artificial · CEU San Pablo · 2026*
