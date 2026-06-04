# 🎬 InfoCine Agent

Crítico de cine personal basado en **Microsoft Agent Framework**.  
Equivalente Python del workflow n8n `InfoCine_mejorado.json`.

---

## Requisitos previos

- Python 3.10 o superior
- Una cuenta de **Azure OpenAI** con un deployment de `gpt-4o-mini`

---

## Instalación

```bash
# 1. Clona o copia los archivos en una carpeta
cd infocine

# 2. (Recomendado) Crea un entorno virtual
python -m venv .venv
source .venv/bin/activate        # Linux / macOS
.venv\Scripts\activate           # Windows

# 3. Instala las dependencias
pip install -r requirements.txt
```

---

## Configuración

```bash
# Copia la plantilla y rellena tus credenciales
cp .env.example .env
```

Edita `.env` con tus valores reales:

| Variable | Dónde encontrarla |
|---|---|
| `AZURE_OPENAI_API_KEY` | portal.azure.com → tu recurso OpenAI → *Keys and Endpoint* |
| `AZURE_OPENAI_ENDPOINT` | misma sección, campo *Endpoint* |
| `OMDB_API_KEY` | [omdbapi.com/apikey.aspx](https://www.omdbapi.com/apikey.aspx) (gratis) |

---

## Uso

```bash
python infocine_agent.py
```

El agente abrirá un chat en la terminal. Ejemplos de preguntas:

```
Tú: Cuéntame todo sobre Inception
Tú: ¿Dónde puedo ver El Padrino en streaming?
Tú: Háblame de Parasite y ponme el tráiler
Tú: salir
```

---

## Herramientas disponibles

| Herramienta | API | Cuándo se activa |
|---|---|---|
| `buscar_peliculas` | OMDb | Siempre, en primer lugar |
| `buscar_detalles_amplios` | TMDB | Tras OMDb, para enriquecer |
| `buscar_trailer_youtube` | YouTube Search | Solo si el usuario pide el tráiler |
| `buscar_plataformas_streaming` | JustWatch ES | Si pregunta dónde ver la película |

---

## Estructura de archivos

```
infocine/
├── infocine_agent.py   # Agente principal
├── requirements.txt    # Dependencias
├── .env.example        # Plantilla de variables de entorno
├── .env                # Tus credenciales (NO subir a git)
└── README.md
```

> **Nota:** Añade `.env` a tu `.gitignore` para no exponer tus claves.
