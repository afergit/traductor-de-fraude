from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Traductor de Fraude API")

# Configurar CORS para permitir peticiones desde la extensión Chrome
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Traductor de Fraude API - Activo"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/analizar")
async def analizar_fraude(texto: str):
    """
    Endpoint para analizar texto y detectar patrones de fraude
    """
    # TODO: Implementar lógica de detección de fraude
    return {
        "texto": texto,
        "es_fraude": False,
        "confianza": 0.0,
        "patrones_detectados": []
    }
