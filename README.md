# Valoralia copilot (MarIA): Asistente conversacional con RAG y agentes

[cite_start]Esta memoria documenta VALORALIA Copilot, al que he llamado MarIA: un asistente conversacional que combina recuperación aumentada por generación (RAG) y un agente con herramientas, construido sobre VALORALIA, el motor de tasación inmobiliaria que desarrollé como Trabajo de Fin de Máster[cite: 20].

## Enlaces del proyecto

[cite_start]Para que se pueda probar el sistema en vivo, dejo aquí los accesos directos al proyecto[cite: 106]:
* [cite_start]**Demo web interactiva (Streamlit):** [MarIA Streamlit](https://valoralia-copilot-demo-marai-nan6wokkfuzmbjcvpmmwl4.streamlit.app/) [cite: 108, 113]
* [cite_start]**Código fuente:** [Google Colab](https://colab.research.google.com/drive/1Cu0X1PYFW4Nnv-6URQETEeO0zkXwhNdQ?usp=sharing) [cite: 86, 109, 114]
* [cite_start]**Motor original del TFM:** [VALORALIA en AWS](http://51.20.2.178/) [cite: 107, 112]
* [cite_start]**Repositorio:** [GitHub](https://github.com/malurosbolea-ux/valoralia-copilot-demo-MarAI) [cite: 110, 115]

## Introducción y motivación

[cite_start]Los modelos de lenguaje son muy capaces, pero cuando no conocen la respuesta tienden a inventarla con total seguridad, lo que se conoce como alucinación[cite: 21]. [cite_start]En un dominio como el inmobiliario eso no es un detalle menor: una cifra equivocada sobre impuestos o sobre normativa tiene consecuencias reales para quien la recibe[cite: 22]. 

[cite_start]Por eso quería un asistente en el que se pudiera confiar[cite: 23]. [cite_start]La técnica del RAG obliga al modelo a responder únicamente a partir de documentos verificados[cite: 24]. [cite_start]Sobre esa base he añadido un agente capaz de razonar y de ejecutar acciones a través de herramientas, una de las cuales es mi propio motor de tasación[cite: 25].

[cite_start]En mi TFM construí el cerebro que predice y en esta práctica construyo el cuerpo que conversa, razona y decide cuándo usar ese cerebro[cite: 36].

## Arquitectura del sistema

[cite_start]El sistema parte de un componente sencillo pero decisivo, el router, que clasifica cada pregunta en dos caminos[cite: 39]:

1. [cite_start]**Información (RAG):** Si la pregunta es informativa (impuestos, normativa, conceptos), la envía al RAG, que responde solo desde la documentación verificada[cite: 40].
2. [cite_start]**Acción (Agente):** Si la pregunta pide una acción (tasar, comparar zonas, agendar una visita), la envía al agente, que razona y ejecuta herramientas[cite: 41].

[cite_start]El RAG, además, está disponible como una herramienta más del agente, un patrón que se conoce como RAG agéntico[cite: 42].

[cite_start]Como modelo generativo empleo Gemini 2.5 Flash, que admite llamada a funciones, una capacidad imprescindible para que el agente decida por sí mismo qué herramienta usar[cite: 48]. [cite_start]Para la base de datos vectorial del RAG utilizo ChromaDB[cite: 51].

## Herramientas del agente

[cite_start]Le he dado cuatro herramientas, cada una definida como una función de Python[cite: 57]:
* [cite_start]**Estimar precio de una vivienda:** Integra mi motor VALORALIA[cite: 58].
* [cite_start]**Comparar zonas:** Devuelve la diferencia de precio por metro cuadrado entre dos municipios[cite: 59].
* [cite_start]**Buscar documentación:** Envuelve el RAG completo[cite: 60].
* [cite_start]**Agendar una visita:** Aplica el patrón human-in-the-loop, preparando la solicitud pero dejándola pendiente de confirmación humana[cite: 61].

## Evaluación

[cite_start]He medido el sistema de dos formas independientes: con el framework oficial RAGAS y con un juez propio basado en un modelo de lenguaje[cite: 64, 65, 66].

| Métrica | Valor | Qué mide |
|---|---|---|
| Faithfulness (RAGAS) | 0.75 | Si la respuesta se apoya en el contexto recuperado y no inventa. |
| Answer relevancy (RAGAS) | 0.90 | Si la respuesta va al grano de lo que se pregunta. |
| Context precision (RAGAS) | 0.88 | De lo recuperado, qué proporción es relevante. |
| Context recall (RAGAS) | 1.00 | De lo relevante, qué proporción se recupera. |
| Fidelidad (juez propio) | 0.93 | Mi propia medida de fidelidad con un LLM como juez. |
| Relevancia (juez propio) | 1.00 | Mi propia medida de relevancia con un LLM como juez. |
| Acierto del router | 100% | Clasificación correcta entre información y acción (6/6). |

[cite_start]*(Datos extraídos de la evaluación del modelo [cite: 68])*

[cite_start]El 0.75 de fidelidad es esperable y no me preocupa, ya que algunas respuestas añaden matices de prudencia (recomendar consultar a un asesor) que no aparecen literalmente en el documento de origen[cite: 73, 74].

## Limitaciones y líneas futuras

[cite_start]Como en todo proyecto, hay limitaciones: la base de conocimiento de esta demo es pequeña (aunque la he ampliado a once páginas [cite: 102][cite_start]) y la herramienta de tasación utiliza valores orientativos por metro cuadrado mientras no conecto el modelo real completo[cite: 78, 80].

[cite_start]Como líneas futuras me planteo conectar el modelo real de VALORALIA, ampliar la documentación con normativa autonómica, dotar a MarIA de memoria de conversación entre turnos y desplegar el asistente sobre la misma infraestructura de AWS donde ya vive el motor de tasación[cite: 85].

---

**Autoría**
Desarrollado por María Luisa Ros Bolea. 
[cite_start]Máster en Big Data e Inteligencia Artificial, CEU San Pablo, 2026[cite: 4, 5].
