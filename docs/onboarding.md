# Onboarding técnico — MCP SupportOps Agent

## Estructura general

El proyecto está dividido en 5 capas:

1. **`client/` (LLM host)**: orquesta conversación, descubre tools MCP y ejecuta tool calls.
2. **`mcp_server/` (capa de herramientas MCP)**: expone tools (`tickets`, `customers`, `security`) y aplica permisos.
3. **`internal_api/` (API HTTP interna)**: implementa endpoints de dominio con FastAPI.
4. **`db/` (persistencia)**: conexión MySQL, esquema SQL y datos semilla.
5. **`app/` (configuración común)**: settings centralizados vía variables de entorno.

Flujo principal: **usuario → `client/agent_host.py` → MCP server → internal API → MySQL**.

## Qué es importante entender primero

- **Configuración centralizada**: `app/config.py` controla puertos, URLs, proveedor LLM y usuario actual simulado (`current_user_id`).
- **Contrato API y tipos**: `internal_api/schemas.py` define modelos de entrada/salida (tickets, clientes, SLA, notas internas).
- **Permisos RBAC**: cada tool MCP invoca `require_permission(...)` antes de acceder a datos.
- **Separación de responsabilidades**:
  - `internal_api/routes/*` resuelve consultas SQL y validaciones HTTP.
  - `mcp_server/tools/*` traduce intención de negocio a llamadas de API interna y formatea salida.
  - `client/agent_host.py` traduce tools MCP al formato de function-calling del LLM.

## Puntos de extensión comunes

- **Agregar nueva capacidad al agente**:
  1. Crear endpoint en `internal_api/routes/`.
  2. Añadir cliente HTTP en `mcp_server/internal_api_client.py`.
  3. Registrar tool en `mcp_server/tools/` con permiso explícito.
  4. Ajustar mensajes/salida en `mcp_server/formatters.py` si aplica.

- **Cambiar proveedor/modelo LLM**:
  - Revisar `client/llm/*` y variables en `.env` (`LLM_PROVIDER`, `OLLAMA_MODE`, modelos base URL).

## Siguiente aprendizaje recomendado

1. Ejecutar el stack local completo (MySQL + API + MCP + host) y hacer un recorrido end-to-end.
2. Leer y probar las tools en `mcp_server/tools/tickets.py` para ver permisos y outputs.
3. Practicar agregando una tool sencilla (ejemplo: filtrar tickets por `assigned_to`).
4. Profundizar en observabilidad/seguridad pendiente del roadmap (`docs/roadmap.md`): auditoría, request IDs y masking.
