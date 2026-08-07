# 05 — Auth (cadastro/login)

Estimativa: 4h · Bloqueada por: 04 · **Status: concluída**

## Objetivo
Cliente final consegue criar conta e logar. Sem tela bonita — funcional.

## Tarefas
- [x] Endpoint de cadastro (cria `User` + `Customer`) — `POST /auth/register`.
- [x] Endpoint de login — `POST /auth/login`. **Decisão**: token DRF
      (`rest_framework.authtoken`), mais simples de integrar num frontend
      separado (React/PWA) do que sessão+cookie.
- [x] Validação básica — e-mail único (case-insensitive) e senha mínima via
      `AUTH_PASSWORD_VALIDATORS` do Django (já configurado, min 8 chars).

## Aceite
- [x] Cadastro cria conta real no banco — testado via curl, cria `User` +
      `Customer` e devolve token.
- [x] Login devolve um token válido — testado via curl.
- [x] Senha errada → 401. E-mail duplicado no cadastro → 400 (validação).

## Decisões
- `username` do Django = e-mail (login é por e-mail, não username separado).
  Evita confundir o cliente com dois campos que fazem a mesma coisa.
- Nome/telefone/endereço exigidos no cadastro (endereço já necessário pro
  fluxo de pedido da task 06 — evita pedir de novo depois).

## Arquivos
`backend/core/serializers.py`, `backend/core/views.py`,
`backend/config/urls.py`, `backend/config/settings.py` (authtoken +
`REST_FRAMEWORK`)
