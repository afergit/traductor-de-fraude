from pydantic import BaseModel, Field, AnyUrl
from typing import List, Optional

# recibe una URL
class RequestAnalizar(BaseModel):
    url: AnyUrl = Field(..., description="URL a analizar (http o https)")

# 2) Info del enlace
class InfoEnlace(BaseModel):
    url_original: Optional[str] = None
    url_final: Optional[str] = None
    es_seguro_httpsO: Optional[bool] = None  # se mantiene el nombre exacto del contrato original
    ssl_cert_valido: Optional[bool] = None   # NUEVO: certificado válido según verificación TLS

# 3) Respuesta
class ResponseAnalizar(BaseModel):
    es_fraude: bool
    titulo: str
    explicacion_simple: str
    tacticas_detectadas: List[str]
    info_enlace: InfoEnlace
