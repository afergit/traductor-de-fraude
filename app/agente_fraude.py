import requests
from requests.exceptions import SSLError, ConnectionError, Timeout, RequestException

from app.schemas import ResponseAnalizar, InfoEnlace

TIMEOUT_SECS = 6

def _investigar_enlace(url: str) -> InfoEnlace:
    """
    Sigue redirecciones y verifica HTTPS y validez del certificado SSL.
    """
    url_original = url
    url_final = url
    es_seguro_https = None
    ssl_valido = None

    try:
        # verify=True => verifica certificado
        resp = requests.get(url, allow_redirects=True, timeout=TIMEOUT_SECS, verify=True)
        url_final = resp.url
        es_seguro_https = url_final.lower().startswith("https://")
        # Si no lanzó SSLError y pudimos conectar con verify=True, asumimos certificado válido
        ssl_valido = True
    except SSLError:
        # Certificado inválido 
        ssl_valido = False
        try:
            resp = requests.get(url, allow_redirects=True, timeout=TIMEOUT_SECS, verify=False)
            url_final = resp.url
            es_seguro_https = url_final.lower().startswith("https://")
        except Exception:
            pass
    except (ConnectionError, Timeout):
        ssl_valido = None
        try:
            resp = requests.get(url, allow_redirects=True, timeout=TIMEOUT_SECS, verify=False)
            url_final = resp.url
            es_seguro_https = url_final.lower().startswith("https://")
        except Exception:
            pass
    except RequestException:
       ssl_valido = None

    return InfoEnlace(
        url_original=url_original,
        url_final=url_final,
        es_seguro_httpsO=es_seguro_https,
        ssl_cert_valido=ssl_valido
    )

async def analizar_url_fraude(url: str) -> ResponseAnalizar:
    info = _investigar_enlace(url)

    tacticas = []
    explicacion = []

    # Criterio 1: HTTPS
    if info.es_seguro_httpsO is False:
        tacticas.append("HTTP sin cifrado")
        explicacion.append("La URL final no usa HTTPS.")

    # Criterio 2: Certificado SSL
    if info.ssl_cert_valido is False:
        tacticas.append("Certificado SSL inválido")
        explicacion.append("El certificado TLS/SSL no es válido o no se pudo verificar.")

    # Heurística simple de riesgo: si cualquiera de los criterios falla, marcamos como fraude/peligro.
    es_fraude = (info.es_seguro_httpsO is False) or (info.ssl_cert_valido is False)

    titulo = "¡Peligro! Esto es una estafa." if es_fraude else "Parece Seguro"
    if not explicacion:
        explicacion.append("La URL usa HTTPS y el certificado es válido (según la verificación realizada).")

    return ResponseAnalizar(
        es_fraude=es_fraude,
        titulo=titulo,
        explicacion_simple=" ".join(explicacion),
        tacticas_detectadas=tacticas,
        info_enlace=info
    )
