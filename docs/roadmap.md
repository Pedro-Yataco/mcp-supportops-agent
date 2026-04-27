# Roadmap

## Phase 1 — Project Foundation

- [ ] Configure Python environment
- [ ] Add environment configuration
- [ ] Add MySQL service with Docker Compose
- [ ] Create initial database schema
- [ ] Add seed data for users, roles, customers, SLAs and tickets

## Phase 2 — Internal API

- [ ] Create FastAPI internal API
- [ ] Add customer endpoints
- [ ] Add ticket endpoints
- [ ] Connect API to MySQL

## Phase 3 — MCP Server

- [ ] Create MCP server with FastMCP
- [ ] Add ticket tools
- [ ] Add customer/SLA tools
- [ ] Add role-based permission checks

## Phase 4 — LLM Host

- [ ] Create Ollama provider
- [ ] Connect LLM host to MCP server
- [ ] Test agent conversations

## Phase 5 — Security & Observability

- [ ] Add tool call audit logs
- [ ] Add request IDs
- [ ] Mask sensitive fields
- [ ] Add admin-only audit tools