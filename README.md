# VALORALIA Copilot - MarIA (demo web)

La cara web de mi asistente. Es el mismo cerebro del notebook (RAG + agente + router),
metido en una interfaz de Streamlit con la que se puede hablar pinchando.

## Arrancarla en mi ordenador
1. pip install -r requirements.txt
2. streamlit run app.py
3. Pego mi clave de Gemini en la barra lateral y a hablar con MarIA.

## Arrancarla desde Google Colab (sin instalar nada en mi PC)
En una celda:
    !pip install -q -r requirements.txt
    !npm install -g localtunnel
    !streamlit run app.py &>/content/log.txt &
    !npx localtunnel --port 8501
Abro el enlace que me da localtunnel y listo.

## Desplegarla gratis (Streamlit Community Cloud)
1. Subo esta carpeta a un repo de GitHub.
2. En share.streamlit.io conecto el repo y elijo app.py.
3. En "Secrets" pego:  GOOGLE_API_KEY = "mi_clave"
4. Deploy. Me da una URL pública para enseñarla en la defensa.

## Conectar el modelo real de VALORALIA
Si dejo mi valoralia_production_B.pkl en la ruta RUTA_MODELO (dentro de app.py),
la herramienta de tasación lo carga solo. Si no está, usa valores orientativos.

Nota: la primera vez tarda un poco porque descarga el modelo de embeddings multilingüe.
