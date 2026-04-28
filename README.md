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

> Nota: el roadmap contempla ampliar seguridad con auditoría y masking.

## Configuración

La configuración se centraliza en `app/config.py` y se alimenta desde `.env` (ver `.env.example`).

Variables relevantes:
- Base de datos: `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD`.
- API interna: `INTERNAL_API_BASE_URL`.
- MCP server: `MCP_SERVER_HOST`, `MCP_SERVER_PORT`.
- Usuario simulado: `CURRENT_USER_ID`.
- LLM/Ollama: `LLM_PROVIDER`, `OLLAMA_MODE`, URLs/modelos local y cloud.

