# 01 — RGPD (consentimento + exclusão de conta)

Bloqueada por: -

## Contexto
Contratado no PDF da proposta: "tratamento técnico de dados pessoais (RGPD) no
código: coleta mínima, consentimento no cadastro, exclusão de conta." Desenho
completo em `docs/RGPD.md` — esta task só implementa o que já está lá.

## Objetivo
Cadastro exige consentimento explícito; cliente final consegue apagar a própria
conta sem quebrar o histórico de pedidos do dono.

## Tarefas
- [ ] Migration: `Customer.consent_accepted_at` (DateTimeField, null=True).
- [ ] `RegisterSerializer` exige `accepts_terms=True` (rejeita cadastro se `False`
      ou ausente).
- [ ] Checkbox obrigatório em `RegisterPage.jsx` (com link pra política de
      privacidade do cliente — pendente URL).
- [ ] Endpoint `DELETE /auth/me` — anonimiza `User`+`Customer` (ver `docs/RGPD.md`
      pro passo a passo exato), apaga token, mantém `Order`/`OrderItem`.
- [ ] Botão "Excluir minha conta" no frontend, com confirmação (modal ou 2º clique
      — não pode ser 1 clique só, ação irreversível).

## Aceite
- [ ] Cadastro sem marcar o checkbox → erro de validação, conta não é criada.
- [ ] Excluir conta → login para de funcionar, `Customer.phone`/
      `delivery_address` viram placeholder, mas os `Order`/`OrderItem` da conta
      continuam visíveis no admin.
- [ ] Testado manualmente: cria conta → faz pedido → exclui conta → confirma no
      admin que o pedido sobrou.

## Arquivos
`backend/core/models.py`, `backend/core/serializers.py`, `backend/core/views.py`,
`backend/config/urls.py`, `frontend/src/pages/RegisterPage.jsx`, nova tela/seção de
conta no frontend.
