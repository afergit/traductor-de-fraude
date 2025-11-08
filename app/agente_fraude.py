import os
import re
import json
import httpx  # Usamos httpx para E/S asincrónica
import google.generativeai as genai
from urllib.parse import urlparse
from httpx import RequestError, TimeoutException

# 1. Configuración de la API Key (desde variables de entorno)
# El servidor (Docker, etc.) debe proveer esta variable.
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    # Esto es crucial. Si no hay API key, el backend no debe iniciar.
    raise ValueError("La variable de entorno GEMINI_API_KEY no está configurada.")

genai.configure(api_key=API_KEY)

# 2. El System Prompt (Definido y validado en Colab)
SYSTEM_PROMPT = """
Eres un motor de análisis de ciberseguridad especializado en detectar estafas (scams) y phishing, diseñado para proteger a usuarios no técnicos.
Tu misión es analizar el texto y la información del enlace proporcionada, y determinar si es un intento de fraude.

**Reglas de Análisis:**
1.  **Detecta Tácticas de Miedo y Urgencia:** Busca frases como "cuenta suspendida", "acción inmediata requerida", "ganaste un premio", "última oportunidad".
2.  **Detecta Suplantación de Autoridad:** ¿Finge ser un banco (BBVA, BCP), una entidad gubernamental (SUNAT), o un servicio popular (Netflix, Google, Microsoft)?
3.  **Analiza el Enlace:** Compara la `url_original` con la `url_final`. ¿Redirige a un dominio inesperado? ¿La `url_final` NO es HTTPS (`es_seguro_httpss`: false)? Esto es una señal de alerta máxima.
4.  **Evalúa el Tono:** Busca errores gramaticales, saludos genéricos ("Estimado usuario") o un tono excesivamente informal o alarmista.

**Formato de Salida Obligatorio:**
Tu respuesta DEBE SER ÚNICAMENTE un objeto JSON válido, sin ningún texto introductorio, explicaciones adicionales o markdown (como ```json).
Usa EXACTAMENTE la siguiente estructura:

{
  "es_fraude": <boolean>,
  "nivel_riesgo": <"Alto", "Medio", "Bajo" o "Nulo">,
  "justificacion": "<Explicación breve y clara del porqué, enfocada en el usuario no técnico>",
  "elementos_detectados": ["<Táctica 1>", "<Táctica 2>", ...]
}
"""

# 3. Modelo de IA Generativa
# Configuramos el modelo para que la respuesta sea solo JSON
generation_config = genai.GenerationConfig(
    response_mime_type="application/json"
)

model = genai.GenerativeModel(
    # Usamos el modelo que SÍ funcionó en Colab
    model_name='gemini-pro-latest',
    system_instruction=SYSTEM_PROMPT,
    generation_config=generation_config
)

# 4. Lógica de Enlaces (Asincrónica con httpx)
async def investigar_enlace_async(url: str, client: httpx.AsyncClient) -> dict:
    """
    Versión asincrónica de la investigación de enlaces usando httpx.
    """
    resultado = {
        "url_original": url,
        "url_final": url,
        "es_seguro_httpss": False, # Corregido (tenía 'httpsO' en el plan original)
        "accesible": False,
        "error": None
    }
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = await client.get(url, allow_redirects=True, timeout=5.0, headers=headers)
        
        response.raise_for_status() # Lanza excepción para 4xx/5xx
        
        url_final = str(response.url) # Convertimos la URL de httpx a string
        parsed_url = urlparse(url_final)
        
        resultado.update({
            "url_final": url_final,
            "es_seguro_httpss": parsed_url.scheme == 'https',
            "accesible": True
        })

    except (RequestError, TimeoutException) as e:
        print(f"Error de red o timeout al investigar enlace: {e}")
        resultado["error"] = f"Error de red o timeout: {str(e)}"
    except Exception as e:
        print(f"Error inesperado al procesar URL: {e}")
        resultado["error"] = f"Error inesperado al procesar URL: {str(e)}"

    return resultado

# 5. Funciones Auxiliares (Regex)
def extraer_urls(texto: str) -> list[str]:
    """
    Extrae todas las URLs encontradas en el texto usando regex.
    """
    # Regex mejorada para capturar URLs (http, https, o www)
    regex = r'(https?://[^\s()<>]+)|(www\.[^\s()<>]+)'
    coincidencias = re.findall(regex, texto)
    
    # re.findall con grupos devuelve tuplas (ej. ('http://...', '') o ('', 'www...'))
    # Necesitamos aplanarlas
    urls_encontradas = [match[0] or match[1] for match in coincidencias]
    
    # Asegurarnos de que las URLs 'www.' tengan un esquema para httpx
    urls_procesadas = []
    for url in urls_encontradas:
        if url.startswith('www.'):
            # Asumimos http para 'www.' si no tiene esquema
            urls_procesadas.append('http://' + url) 
        else:
            urls_procesadas.append(url)
            
    return urls_procesadas


def construir_prompt_dinamico(texto_usuario, info_enlace=None):
    """
    Construye el prompt que se enviará al LLM.
    """
    # Convertimos el dict de info_enlace a un string JSON para el prompt
    info_enlace_str = json.dumps(info_enlace, indent=2) if info_enlace else "No se encontraron enlaces en el texto."
    
    return f"""
    --- INICIO DEL ANÁLISIS ---

    **Texto a Analizar:**
    "{texto_usuario}"

    **Información del Enlace (si existe):**
    {info_enlace_str}

    --- FIN DEL ANÁLISIS ---
    
    Por favor, genera tu análisis en el formato JSON requerido.
    """

# 6. Función Principal (La que importa Persona 2)
async def analizar_texto_fraude(texto_recibido: str) -> dict:
    """
    Función principal que orquesta el análisis de fraude.
    """
    info_enlace = None
    
    # 1. Extraer URLs
    urls = extraer_urls(texto_recibido)
    
    # 2. Investigar la *primera* URL encontrada (si existe)
    if urls:
        # Usamos un AsyncClient para manejar la conexión eficientemente
        # Esto es clave para el rendimiento en un servidor async
        async with httpx.AsyncClient() as client:
            info_enlace = await investigar_enlace_async(urls[0], client)
            
    # 3. Construir el prompt final
    prompt_final = construir_prompt_dinamico(texto_recibido, info_enlace)
    
    # 4. Llamar a la API de Gemini (de forma asincrónica)
    try:
        response = await model.generate_content_async(prompt_final)
        
        # 5. Procesar la respuesta
        # Gracias a `response_mime_type="application/json"`,
        # la respuesta YA es un JSON.
        
        # Cargamos el JSON para poder manipularlo
        resultado_json = json.loads(response.text)
        
        # Adjuntamos la información del enlace al resultado final
        # para que el frontend pueda mostrarla si es necesario.
        resultado_json['info_enlace'] = info_enlace
        
        return resultado_json

    except json.JSONDecodeError as e:
        print(f"Error Crítico: El LLM no devolvió un JSON válido. Respuesta: {response.text}")
        return {
            "es_fraude": True,
            "nivel_riesgo": "Indeterminado",
            "justificacion": "Error al procesar la respuesta del motor de análisis. Por favor, ten precaución.",
            "elementos_detectados": ["Error de Análisis"],
            "info_enlace": info_enlace
        }
    except Exception as e:
        print(f"Error Crítico al llamar al LLM: {e}")
        return {
            "es_fraude": True,
            "nivel_riesgo": "Indeterminado",
            "justificacion": f"Error al contactar al motor de análisis: {e}",
            "elementos_detectados": ["Error de Análisis"],
            "info_enlace": info_enlace
        }
