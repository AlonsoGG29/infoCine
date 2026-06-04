import os
import asyncio
import json
import requests
from dotenv import load_dotenv
from agent_framework import Agent
# OpenAIChatCompletionClient usa /chat/completions, compatible con Azure.
# OpenAIChatClient usa la nueva Responses API que Azure NO soporta.
from agent_framework.openai import OpenAIChatCompletionClient

load_dotenv()

# ─────────────────────────────────────────────
# HERRAMIENTAS (simulan los nodos HTTP de n8n)
# ─────────────────────────────────────────────

def buscar_peliculas(titulo: str) -> str:
    """OMDb API: devuelve sinopsis, año, director, actores, duración, género, score IMDb y país.
    Úsala SIEMPRE en primer lugar."""
    api_key = os.environ.get("OMDB_API_KEY", "fd822fa2")
    url = f"https://www.omdbapi.com/?apikey={api_key}&t={titulo}&type=movie"
    r = requests.get(url)
    return json.dumps(r.json()) if r.status_code == 200 else f"Error OMDb: {r.text}"


def buscar_detalles_amplios(titulo: str) -> str:
    """TMDB: elenco completo, presupuesto, recaudación, géneros detallados y películas similares.
    Úsala DESPUÉS de buscar_peliculas para enriquecer la ficha."""
    url = f"https://www.themoviedb.org/search/movie?query={titulo}&language=es-ES"
    r = requests.get(url)
    return str(r.text[:2000]) if r.status_code == 200 else f"Error TMDB: {r.text}"


def buscar_trailer_youtube(titulo: str) -> str:
    """YouTube: enlace de búsqueda al tráiler oficial en español.
    Úsala SOLO si el usuario pide el tráiler explícitamente."""
    query = titulo.replace(" ", "+") + "+trailer+oficial+español"
    return f"https://www.youtube.com/results?search_query={query}"


def buscar_plataformas_streaming(titulo: str) -> str:
    """JustWatch: disponibilidad en Netflix, Prime Video, HBO, Disney+, etc. en España.
    Úsala si el usuario pregunta dónde ver la película."""
    query = titulo.replace(" ", "%20")
    return f"https://www.justwatch.com/es/buscar?q={query}"


# ─────────────────────────────────────────────
# AGENTE PRINCIPAL
# ─────────────────────────────────────────────

SYSTEM_MESSAGE = """Eres un CRÍTICO DE CINE PROFESIONAL y CINÉFILO DE ELITE con profundos conocimientos sobre
narrativa cinematográfica, dirección, cinematografía, edición, sound design y movimientos artísticos.
Tu objetivo es ayudar al usuario a DESCUBRIR, ENTENDER y DISFRUTAR las películas.

ORDEN DE EJECUCIÓN OBLIGATORIO:
1. SIEMPRE primero: buscar_peliculas (información base)
2. LUEGO: buscar_detalles_amplios (enriquecimiento)
3. DESPUÉS: buscar_trailer_youtube (SOLO si el usuario lo solicita)
4. FINALMENTE: buscar_plataformas_streaming (si pregunta dónde ver)

ESTRUCTURA DE RESPUESTA:
📽️ Sinopsis → Ficha Técnica → Elenco → Análisis Cinematográfico →
   Contexto Histórico/Artístico → Recomendaciones Similares → Dónde Ver

REGLAS CRÍTICAS:
- NUNCA inventes datos; usa exclusivamente lo que devuelvan las herramientas.
- Tono entusiasta, accesible pero erudito. Haz que el usuario quiera verla.
- Clásicos: añade contexto de época y relevancia. Blockbusters: destaca espectacularidad.
- Indie: valora la originalidad y el riesgo artístico.
- ESPERA a que una herramienta termine antes de llamar a la siguiente."""


async def main():
    # ── Extraemos solo el base URL del endpoint completo que viene en el .env ──
    # .env tiene: https://hugo-taller-swc.cognitiveservices.azure.com/openai/deployments/...
    # El framework necesita solo: https://hugo-taller-swc.cognitiveservices.azure.com/
    raw_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
    base_endpoint = raw_endpoint.split("/openai/")[0] + "/"

    # OpenAIChatCompletionClient → llama a /chat/completions, soportado por Azure
    client = OpenAIChatCompletionClient(
        model="gpt-4o-mini",
        api_key=os.environ.get("AZURE_OPENAI_API_KEY", ""),
        azure_endpoint=base_endpoint,
        api_version="2025-01-01-preview"
    )

    # ── Creación del agente con sus 4 herramientas ──
    agente = Agent(
        client=client,
        name="InfoCine_Agent",
        instructions=SYSTEM_MESSAGE,
        tools=[
            buscar_peliculas,
            buscar_detalles_amplios,
            buscar_trailer_youtube,
            buscar_plataformas_streaming,
        ]
    )

    # ── Bucle de conversación (simula el chat trigger de n8n) ──
    print("🎬 InfoCine — Tu crítico de cine personal. Escribe 'salir' para terminar.\n")
    while True:
        user_input = input("Tú: ").strip()
        if user_input.lower() in ("salir", "exit", "quit"):
            break
        if not user_input:
            continue

        resultado = await agente.run(user_input)
        print(f"\nInfoCine:\n{resultado.text}\n{'─'*60}\n")


if __name__ == "__main__":
    asyncio.run(main())
