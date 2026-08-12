# 01 — RGPD (consentimento + exclusão de conta)

Bloqueada por: - · **Status: concluída**

## Contexto
Contratado no PDF da proposta: "tratamento técnico de dados pessoais (RGPD) no
código: coleta mínima, consentimento no cadastro, exclusão de conta." Desenho
completo em `docs/RGPD.md` — esta task só implementa o que já está lá.

## Objetivo
Cadastro exige consentimento explícito; cliente final consegue apagar a própria
conta sem quebrar o histórico de pedidos do dono.

## Tarefas
- [x] Migration: `Customer.consent_accepted_at` (DateTimeField, null=True).
- [x] `RegisterSerializer` exige `accepts_terms=True` (rejeita cadastro se `False`
      ou ausente — `validate_accepts_terms`).
- [x] Checkbox obrigatório em `RegisterPage.jsx` (`required` HTML5 + validação
      backend). Link pra política de privacidade **não incluído** — cliente ainda
      não mandou a URL; texto fica só descritivo até lá.
- [x] Endpoint `DELETE /auth/me` — anonimiza `User`+`Customer` (ver `docs/RGPD.md`),
      apaga token, mantém `Order`/`OrderItem`.
- [x] Botão "Excluir minha conta" — nova tela `/conta` (`AccountPage.jsx`), com
      confirmação em 2 passos (não é 1 clique só).

## Aceite
- [x] Cadastro sem marcar o checkbox → bloqueado no frontend (HTML5 `required`) E
      no backend (testado direto via API, contorna o frontend) → 400.
- [x] Excluir conta → token invalidado de verdade (testado via HTTP real: mesmo
      token depois da exclusão devolve 401 "Invalid token"), `Customer.phone`/
      `delivery_address` viram `"[dado removido]"`, `Order`/`OrderItem` continuam
      intactos.
- [x] Testado ao vivo ponta a ponta (Playwright dirigindo o frontend real): cadastro
      com checkbox → login → Minha conta → excluir → confirma → sessão morta, nav
      volta pra "Entrar/Cadastrar". Sem erro de console.

## Arquivos
`backend/core/models.py`, `backend/core/serializers.py`, `backend/core/views.py`,
`backend/config/urls.py`, `frontend/src/pages/RegisterPage.jsx`, nova tela/seção de
conta no frontend.
