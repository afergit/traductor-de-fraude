from dotenv import load_dotenv

# Carga el .env ANTES que cualquier otra cosa
load_dotenv()

# Ahora sí, importa el resto de tu app
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import Settings, get_cors_origins
from app.routers import analyzer

def create_app() -> FastAPI:
    cfg = Settings() # Esta línea ahora funcionará
    app = FastAPI(
        title="Detector de fraude",
        version="1.0",
        description="API para analizar un enlace (HTTP→HTTPS y certificado SSL)"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_cors_origins(cfg),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(analyzer.router)
    return app

app = create_app()