from typing import Callable, Awaitable
from app.agente_fraude import analizar_url_fraude

def get_analyzer() -> Callable[[str], Awaitable]:
    return analizar_url_fraude
