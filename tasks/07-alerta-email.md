# 07 — Alerta por e-mail em novo pedido

Estimativa: 3h · Bloqueada por: 06 · **Status: concluída**

## Objetivo
Dono/funcionário sabe na hora que chegou pedido novo, pra comprar no fornecedor a
tempo (estoque não é garantido — quanto mais rápido, melhor).

## Tarefas
- [x] Configurar envio de e-mail — `core/email_utils.py`, mesmo padrão
      (thread + retry) usado em outro projeto do freela (`Salonix/core/
      email_utils.py`, referência). **Decisão**: backend configurável via env
      (`EMAIL_BACKEND`), default = console backend (imprime no terminal, sem
      precisar de conta SMTP pra rodar localmente); produção troca via env pro
      SMTP real.
- [x] Disparar e-mail pro(s) e-mail(s) da equipe (`TEAM_ALERT_EMAILS`) a cada
      `Order` criado, com dados do pedido (produto, cliente, telefone,
      endereço, preço de custo/venda).

## Aceite
- [x] Criar pedido dispara o e-mail — testado (console backend), conteúdo
      correto (cliente, itens, preço com margem).
- [x] Testado com SMTP real (Gmail + senha de app) — e-mail chegou na caixa
      de entrada, formatação e dados corretos (screenshot confirmado pelo
      usuário).

## Decisão pendente: link direto pro produto
Task original pedia "link pro produto no dtsshop.de pra comprar". **Não
incluído** — não temos confirmado o padrão de URL de produto do dtsshop.de
(só validamos os endpoints JSON/HTML de listagem, não a página de detalhe
individual). E-mail inclui o `id` do fornecedor e instrui buscar manualmente.
Ver `investigar.md`.

## Achado de segurança (endereçado)
Revisão automática apontou HTML injection no e-mail — campos vindos do
cliente (telefone, endereço, nome do produto) eram interpolados direto no
HTML. Corrigido com `format_html`/`format_html_join` (escapa automaticamente).
Testado com payload `<script>`/`<img>` — escapado corretamente na versão
HTML (texto plano não precisa, não é renderizado como marcação).

## Arquivos
`backend/core/email_utils.py`, `backend/core/views.py`,
`backend/config/settings.py`, `backend/.env.example`
