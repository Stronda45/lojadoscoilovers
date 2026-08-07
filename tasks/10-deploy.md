# 10 — Deploy (Railway — backend + frontend)

Estimativa: 3h → **revisar para ~5h** (Playwright no Railway adiciona trabalho, ver
abaixo) · Bloqueada por: 08, 09

## Objetivo
Sistema acessível fora do ambiente local, pro cliente testar de verdade.

## Decisão (2026-08-07): tudo no Railway, não Vercel+Railway
Frontend também iria pro Vercel originalmente. Mudado pra **2 serviços dentro
do mesmo projeto Railway** (backend+banco e frontend) — Railway roda
container completo, então serve tanto o backend (que precisa de Playwright,
não cabe em serverless) quanto um frontend estático sem problema. Motivo da
troca: 1 conta/1 fatura é mais simples pro cliente (não-técnico) do que
gerenciar 2 plataformas — não é uma questão de custo (frontend estático
seria ~R$0 no Vercel Free de qualquer forma).

## Tarefas
- [ ] Backend (Django+DRF) no Railway — DB Postgres também no Railway.
- [ ] **Backend precisa de Dockerfile custom** (não o build automático padrão do
      Railway) — ver seção Playwright abaixo.
- [ ] Frontend (React) como 2º serviço no mesmo projeto Railway (build estático
      + servidor simples, ex: Caddy/serve), apontando pra URL do backend em
      produção via `VITE_API_BASE_URL`.
- [ ] Variáveis de ambiente configuradas nos dois (SMTP, DB, CORS de produção).
- [ ] Confirmar: hospedagem é custo do cliente (já avisado na proposta) — usar o
      cartão/conta dele, não a sua.

## Playwright no Railway — o que muda

A task 03 (listagem de produtos) precisa de Chromium real rodando no servidor, não só
a lib Python. Isso tem 3 impactos que precisam ser documentados pro cliente:

### 1. Build/imagem
O build automático do Railway (Nixpacks) não instala as dependências de sistema que o
Chromium precisa (libs gráficas, fontes, etc.). Solução: `Dockerfile` próprio partindo
da imagem oficial do Playwright (`mcr.microsoft.com/playwright/python:v1.62.0-noble`,
mesma versão do `requirements.txt`), que já vem com tudo pronto. Railway builda
Dockerfile customizado nativamente, sem configuração especial.

### 2. Código — ajuste necessário pra rodar em container
Container do Railway roda como root — Chromium recusa rodar como root sem a flag
`--no-sandbox`. Localmente (Mac, usuário normal) isso não é necessário. Precisa
adicionar esse argumento condicionalmente (ex: via variável de ambiente) em
`_extract_products_via_browser` (`core/connectors/dtsshop.py`) antes do deploy.

### 3. Custo e desempenho — avisar o cliente
- **Imagem maior**: a imagem do Playwright é bem mais pesada (~1-2GB) que um
  container Python comum (~150MB) — build mais lento, mais espaço.
- **Memória/CPU maior**: cada chamada de busca abre um Chromium de verdade
  (`chromium.launch()` por request — ver `investigar.md`, item de otimização
  futura). Isso consome bem mais RAM/CPU que uma rota Django comum. Em volume baixo
  (uso inicial do cliente) deve caber no plano de entrada do Railway, mas é
  **provável que o custo mensal fique mais alto** do que um backend Django "normal"
  sem Playwright — não temos número exato de antemão, precisa acompanhar a fatura
  nos primeiros dias e ajustar (plano maior, ou otimizar o reuso do browser) se
  necessário.
- **Latência**: buscas que passam pelo Playwright (listagem de produtos) demoram
  alguns segundos a mais que uma chamada JSON comum (get_categories, preço/estoque),
  porque abrem um navegador de verdade a cada vez. Isso é esperado, não é bug —
  avisar o cliente pra não estranhar a busca ser mais lenta que o preço/estoque.

## Aceite
- [ ] Fluxo completo (cadastro → busca → pedido → e-mail) funcionando em produção.
- [ ] Busca (via Playwright) funcionando em produção, não só localmente.
- [ ] Cliente avisado sobre o impacto de custo/latência do Playwright antes do
      lançamento (não depois, na fatura).

## Pendências antes de começar (aguardando o cliente)
- E-mail (colaborador no repositório GitHub)
- Conta Railway (+ cartão — plano pago, ver acima)
- Domínio desejado
- E-mail/SMTP de produção pro alerta de pedido (não pode ser conta pessoal
  do freelancer)
- Valores da margem por faixa de preço (`investigar.md`)
