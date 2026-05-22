# VALORALIA Copilot: MarIA 🏠✨

*El asistente que conversa, razona y tasa.*

Hola, soy **María Luisa Ros Bolea**. Este repositorio contiene el código y la documentación de **VALORALIA Copilot** (a quien he bautizado como MarIA), la capa conversacional de mi Trabajo de Fin de Máster en Big Data e Inteligencia Artificial. 

Puedes conectar conmigo y conocer más sobre mi trayectoria combinando la estrategia digital, el análisis de datos y la inteligencia artificial aquí:
* 💼 [LinkedIn](https://www.linkedin.com/in/mar%C3%ADa-luisa-ros-bolea-400780160/)
* 🌐 [Portfolio Digital](https://malurosbolea-ux.github.io/digital-strategy-portfolio/)

---

## El proyecto: del motor que predice al producto que conversa

En mi TFM desarrollé **VALORALIA**, un modelo automatizado de valoración (AVM) híbrido que estima el precio de la vivienda en Madrid combinando datos tabulares y visión artificial a través de redes neuronales (ResNet50). Sin embargo, un modelo predictivo le habla a una API, no a una persona.

Con **MarIA**, he construido el cuerpo que conversa. Es un asistente conversacional que soluciona el problema de las "alucinaciones" (invenciones de los modelos de lenguaje) en el crítico sector inmobiliario. Lo logra combinando **RAG (Retrieval-Augmented Generation)** y un **Agente ReAct** con llamada a herramientas. Ahora, el modelo de tasación no es un ente aislado, sino una herramienta fundamental dentro de un sistema interactivo y seguro.

## Arquitectura del sistema

El núcleo de MarIA toma decisiones en tiempo real para ofrecer respuestas fiables y estructuradas:

1.  **Router inteligente:** Clasifica la intención del usuario. Si busca información (normativa, impuestos, zonas), lo envía al sistema RAG. Si busca una acción (tasar, agendar), activa al agente.
2.  **Sistema RAG (Cero alucinaciones):** Responde *exclusivamente* basándose en una base de conocimiento verificada (utilizando ChromaDB y embeddings multilingües). Si no tiene el dato, lo reconoce con total honestidad.
3.  **Agente ReAct:** Sigue el ciclo analítico de *pensar, actuar y observar*. Dispone de cuatro herramientas clave:
    * **Estimar precio:** Conecta directamente con el motor de VALORALIA.
    * **Comparar zonas:** Analiza y compara diferencias de precio por metro cuadrado.
    * **Buscar documentación:** Utiliza el RAG completo como una herramienta más (patrón de *RAG agéntico*).
    * **Agendar visita:** Implementa un sistema *Human-in-the-loop*; el agente prepara la solicitud pero requiere confirmación de una persona humana antes de cerrarla definitivamente.

## Evaluación y resultados

Casi nadie evalúa su RAG, pero para mí ahí reside la diferencia entre un trabajo correcto y uno excelente. He medido el sistema de forma rigurosa empleando el framework oficial RAGAS y un juez propio basado en LLM:

| Métrica | Valor | Qué mide |
| :--- | :--- | :--- |
| **Context recall (RAGAS)** | 1.00 | De lo relevante, qué proporción se recupera. |
| **Answer relevancy (RAGAS)** | 0.90 | Si la respuesta va al grano de lo que se pregunta. |
| **Fidelidad (Juez propio LLM)** | 0.93 | Mi propia medida de fidelidad comprobada con un modelo actuando como juez. |
| **Acierto del router** | 100% | Clasificación perfecta entre consultas de información y de acción. |

## Stack tecnológico

Para crear una experiencia fluida y unificada, he utilizado las siguientes piezas:
* **LLM & Agentes:** Gemini 2.5 Flash, LangChain, LangGraph.
* **Vectores y Embeddings:** ChromaDB, Sentence-Transformers (HuggingFace).
* **Interfaz Web:** Streamlit (diseñada con una estética cuidada, combinando tonos *navy* con detalles en rosa pastel para reflejar la identidad visual de la marca).
* **Machine Learning (Core):** XGBoost, ResNet50 (propios del motor de valoración VALORALIA).

---

## Instalación y despliegue paso a paso

Si quieres probar a MarIA, te lo dejo todo preparado para que lo hagas sin complicaciones, paso a paso:

### Opción 1: En tu ordenador local
1.  Clona este repositorio en tu equipo.
2.  Instala las dependencias necesarias ejecutando:
    ```bash
    pip install -r requirements.txt
    ```
3.  Lanza la aplicación de Streamlit:
    ```bash
    streamlit run app.py
    ```
4.  Pega tu clave de Google Gemini en la barra lateral de la interfaz y empieza a hablar con MarIA.

### Opción 2: Desde Google Colab (Sin instalar nada)
Si prefieres no instalar nada, ejecuta este bloque en una celda de un notebook de Colab:
```bash
!pip install -q -r requirements.txt
!npm install -g localtunnel
!streamlit run app.py &>/content/log.txt &
!npx localtunnel --port 8501
