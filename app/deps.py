from typing import Callable, Awaitable
from app.agente_fraude import analizar_texto_fraude

def get_analyzer() -> Callable[[str], Awaitable]:
    return analizar_texto_fraude
