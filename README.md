# MCP SupportOps Agent

Mini proyecto empresarial para explorar el uso de Model Context Protocol (MCP) en un escenario de soporte técnico.

El objetivo es construir un agente de IA que pueda consultar una base de datos MySQL y una API interna simulada mediante herramientas MCP, aplicando controles básicos de usuarios, roles y permisos.

## Stack

- Python
- MCP / FastMCP
- MySQL
- Ollama para desarrollo local
- Anthropic Claude como provider opcional futuro
- FastAPI para API interna simulada

## Funcionalidades iniciales

- Consulta de tickets de soporte
- Consulta de clientes y SLA
- Control de permisos por rol
- Tools MCP protegidas
- Arquitectura preparada para auditoría futura

## Arquitectura prevista

Usuario → LLM Host → MCP Client → MCP Server → MySQL + API interna simulada