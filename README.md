# MCP SupportOps Agent

Proyecto de referencia para construir un agente de soporte técnico con **Model Context Protocol (MCP)**, una **API interna** y **MySQL**, con enfoque en seguridad básica por roles y evolución hacia observabilidad/auditoría.

## Objetivo

Demostrar un flujo de soporte empresarial donde un host LLM:

1. interpreta la intención del usuario,
2. descubre y ejecuta herramientas MCP,
3. consulta/actualiza datos operativos vía API interna,
4. y respeta permisos según el usuario simulado activo.

## Arquitectura (vista rápida)

```text
Usuario
  ↓
LLM Host (client/agent_host.py)
  ↓
MCP Server (mcp_server/server.py + mcp_server/tools/*)
  ↓
Internal API (internal_api/api.py + internal_api/routes/*)
  ↓
MySQL (db/schema.sql + db/seed.sql)
```

## Estructura del repositorio

- `app/`: configuración central (`Settings`) desde `.env`.
- `client/`: host conversacional y puente de tool-calling LLM ↔ MCP.
- `mcp_server/`: servidor MCP, tools de negocio, formatters y cliente de API interna.
- `internal_api/`: API FastAPI con endpoints de tickets, clientes y SLA.
- `db/`: conexión a base de datos, esquema SQL y datos de ejemplo.
- `docs/`: roadmap y documentación de onboarding.

## Componentes principales

### 1) Host LLM (`client/`)

- Usa MCP client HTTP (`/mcp`) para listar tools disponibles.
- Convierte tools MCP a formato function-calling del provider LLM.
- Ejecuta tool calls y reinyecta resultados al modelo para respuesta final.

Archivo clave: `client/agent_host.py`.

### 2) MCP Server (`mcp_server/`)

- Expone tools de dominio (tickets, clientes, seguridad).
- Aplica control de permisos antes de cualquier operación sensible.
- Consume la API interna vía `httpx` y retorna salida en formato legible/JSON.

Archivos clave:
- `mcp_server/server.py`
- `mcp_server/tools/tickets.py`
- `mcp_server/tools/customers.py`
- `mcp_server/tools/security.py`
- `mcp_server/internal_api_client.py`

### 3) Internal API (`internal_api/`)

- Define endpoints REST para listar/consultar tickets y clientes.
- Incluye operación de negocio para detectar riesgo de SLA en tickets abiertos/en progreso.
- Usa consultas SQL parametrizadas y validación de entrada/salida con Pydantic.

Archivos clave:
- `internal_api/api.py`
- `internal_api/routes/tickets.py`
- `internal_api/routes/customers.py`
- `internal_api/schemas.py`

### 4) Capa de datos (`db/`)

- `db/schema.sql`: estructura base de tablas.
- `db/seed.sql`: datos iniciales para pruebas locales.
- `db/connection.py`: manejo de conexión/cursor con commit/rollback automático.

## Seguridad y permisos

El proyecto usa un enfoque RBAC básico a nivel de tools MCP:

- La identidad activa se simula con `current_user_id` en configuración.
- Cada tool valida permisos explícitos (ej. `tickets.read`, `customers.read`, `sla.read`, `tickets.comment.internal`, `sla.risk.detect`).
- Si un permiso falla, la tool no ejecuta la acción sobre datos.

## Configuración

La configuración se centraliza en `app/config.py` y se alimenta desde `.env` (ver `.env.example`).

Variables relevantes:
- Base de datos: `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD`.
- API interna: `INTERNAL_API_BASE_URL`.
- MCP server: `MCP_SERVER_HOST`, `MCP_SERVER_PORT`.
- Usuario simulado: `CURRENT_USER_ID`.
- LLM/Ollama: `LLM_PROVIDER`, `OL_MODE`, URLs/modelos local y cloud.



## Cómo levantar y probar el proyecto (paso a paso)

> Recomendación: usa **4 terminales** para separar procesos y facilitar troubleshooting.

### 0) Prerrequisitos

- Python 3.11+.
- Docker y Docker Compose.
- Dependencias Python instaladas (por ejemplo con `pip install -r requirements.txt`).
- Archivo `.env` creado a partir de `.env.example`.

```bash
cp .env.example .env
```

### 1) Configurar el modelo LLM en `.env`

Este proyecto hoy soporta `LLM_PROVIDER=ollama`.

#### Opción A: Ollama local

1. Asegúrate de tener el daemon de Ollama activo.
2. Descarga el modelo que quieras usar (ejemplos):

```bash
ollama pull qwen2.5:7b
# o
ollama pull llama3.1:8b
```

3. Ajusta `.env`:

```env
LLM_PROVIDER=ollama
OL_MODE=local
OL_LOCAL_BASE_URL=http://localhost:11434
OL_LOCAL_MODEL=qwen2.5:7b   # o el modelo que descargaste
```

> Si cambias de modelo, recuerda actualizar `OL_LOCAL_MODEL` para que coincida exactamente con el nombre/tag descargado en Ollama.

#### Opción B: Ollama Cloud

Configura `.env` así:

```env
LLM_PROVIDER=ollama
OL_MODE=cloud
OL_CLOUD_BASE_URL=https://ollama.com
OL_CLOUD_MODEL=qwen3.5:397b-cloud
OL_API_KEY=tu_api_key_aqui
```

> En modo cloud, `OL_API_KEY` es obligatorio y el modelo se toma de `OL_CLOUD_MODEL`.

### 2) Levantar la base de datos con Docker

En una terminal:

```bash
docker compose up -d
```

Comandos útiles:

```bash
docker compose ps
docker compose logs -f
```

Para reiniciar desde cero (borra volúmenes/datos):

```bash
docker compose down -v
docker compose up -d
```

### 3) Levantar la Internal API

En otra terminal:

```bash
uvicorn internal_api.api:app --reload --port 8001
```

### 4) Levantar el MCP Server

En otra terminal:

```bash
python -m mcp_server.server
```

### 5) Levantar el Agent Host (chat)

En otra terminal:

```bash
python -m client.agent_host
```

Si todo está bien, deberías poder escribir preguntas en consola y recibir respuestas que pueden incluir consultas a tools MCP.

## Flujo rápido de verificación

1. `docker compose up -d`
2. `uvicorn internal_api.api:app --reload --port 8001`
3. `python -m mcp_server.server`
4. `python -m client.agent_host`
5. Probar prompts de ejemplo (abajo).

## Prompts de ejemplo para probar el agente

- "Muéstrame los tickets abiertos del cliente 1".
- "¿Qué tickets están en riesgo de SLA?".
- "Dame un resumen del cliente 2".
- "Agrega un comentario interno al ticket 3: 'Contactar al cliente para validar workaround'."
- "¿Qué permisos tengo disponibles para operar tickets y clientes?"

## Troubleshooting rápido

- Si falla conexión a MySQL, valida que `MYSQL_PORT` en `.env` coincida con `docker-compose.yml`.
- Si el host no encuentra el MCP server, valida `MCP_SERVER_HOST` y `MCP_SERVER_PORT`.
- Si falla el modelo local, confirma que Ollama esté activo y que `OL_LOCAL_MODEL` exista (`ollama list`).
- Si falla cloud, revisa `OL_API_KEY`, `OL_CLOUD_BASE_URL` y `OL_CLOUD_MODEL`.
- Si cambias `.env`, reinicia los procesos Python para recargar configuración.
