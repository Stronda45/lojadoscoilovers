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

## Addendum (2026-08-07) — revisão de segurança
Revisão automática no commit apontou 3 achados, endereçados:
- **Sem rate limit em login/cadastro** (risco de força bruta) — `ScopedRateThrottle`
  adicionado (`login`: 5/min, `register`: 10/hora, `config/settings.py`).
- **Token sem forma de invalidar** — endpoint `POST /auth/logout` adicionado
  (apaga o token atual). Token DRF continua sem expiração automática (aceito
  pro escopo da Fase 1).
- **Enumeração de e-mail no cadastro** (`"Já existe uma conta com este e-mail"`
  revela se o e-mail já está cadastrado) — decisão: manter. É padrão de
  mercado em cadastro (Google, GitHub fazem igual) e necessário pra UX (cliente
  precisa saber que já tem conta e deve logar em vez de cadastrar de novo).
  Diferente de enumeração no *login*, que não temos (mensagem de erro genérica
  já cobre isso).

## Arquivos
`backend/core/serializers.py`, `backend/core/views.py`,
`backend/config/urls.py`, `backend/config/settings.py` (authtoken +
`REST_FRAMEWORK`)
