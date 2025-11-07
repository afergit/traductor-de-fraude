from fastapi import APIRouter, Depends, HTTPException
from typing import Callable, Awaitable

from app.schemas import RequestAnalizar, ResponseAnalizar, InfoEnlace
from app.deps import get_analyzer

router = APIRouter(prefix="", tags=["analyzer"])

@router.post("/analizar", response_model=ResponseAnalizar)
async def analizar(
    payload: RequestAnalizar,
    analyzer: Callable[[str], Awaitable[ResponseAnalizar]] = Depends(get_analyzer),
):
    try:
        # ahora pasamos la URL directamente al agente
        return await analyzer(str(payload.url))
    except Exception as ex:
        raise HTTPException(status_code=500, detail="Error interno del análisis") from ex

@router.post("/analizar-mock", response_model=ResponseAnalizar)
async def analizar_mock(payload: RequestAnalizar):
    # - Si la URL empieza con http:// => no es https => potencial riesgo
    # - ssl_cert_valido lo marcamos como None en el mock simple (o False si quieres enfatizar)
    url = str(payload.url)
    es_https = url.lower().startswith("https://")

    tacticas = []
    if not es_https:
        tacticas.append("HTTP sin cifrado")

    titulo = "¡Peligro! Esto es una estafa." if not es_https else "Parece Seguro"
    explicacion = (
        "La conexión no usa HTTPS; podría ser insegura."
        if not es_https else
        "La URL usa HTTPS "
    )

    return ResponseAnalizar(
        es_fraude=not es_https,
        titulo=titulo,
        explicacion_simple=explicacion,
        tacticas_detectadas=tacticas,
        info_enlace=InfoEnlace(
            url_original=url,
            url_final=url,             
            es_seguro_httpsO=es_https, 
            ssl_cert_valido=None       
        ),
    )

@router.get("/health")
async def health():
    return {"status": "ok"}
