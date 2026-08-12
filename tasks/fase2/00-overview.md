# Fase 2 — RGPD, painel, testes e acabamento

Prazo: 4-5 semanas a partir da aprovação/pagamento da Fase 1 (`proposta-v2-
intermediario.pdf`, €1.200). Fase 1 já foi validada pelo cliente localmente
(sem deploy ainda — deploy entra nesta fase, junto com o início real dela).

## Ordem de execução

| # | Tarefa | Bloqueada por |
|---|--------|---------------|
| 01 | RGPD (consentimento + exclusão de conta) | - |
| 02 | Painel admin (Django Admin + grupo "Funcionário") | - |
| 03 | Testes automatizados (conector dtsshop.de) | - |
| 04 | Import de Excel/CSV | **bloqueada** — ver abaixo |
| 05 | Design de verdade (identidade visual) | **bloqueada** — ver abaixo |
| — | Deploy real (Railway, backend+frontend) | 01, 02, 03 |

01, 02 e 03 não dependem de resposta do cliente — podem começar assim que a Fase 2
for aprovada/paga. 04 e 05 estão bloqueadas por pendências externas (ver cada task).

## Bloqueios ativos

- **Task 04 (Excel/CSV)**: não estava no escopo original do PDF da proposta — surgiu
  numa conversa à parte. Precisa (a) alinhar com o cliente se entra nos €1.200 ou é
  cobrado à parte, (b) respostas da seção 7 de
  `/Users/pablo/Project/famaInPecas/perguntas-para-cliente.txt`. Desenho técnico
  completo já em `docs/EXCEL-IMPORT.md`, pronto pra quando destravar.
- **Task 05 (Design)**: aguardando do cliente nome final da marca, logo, paleta de
  cores (`questionario.txt`, 5.1 — marca existe mas nome vai mudar, sem assets
  ainda).

## Também pendente (não bloqueia início, mas precisa de resposta antes de fechar)
- Valores da margem por faixa de preço (`investigar.md`).
- Domínio, conta Railway, e-mail/SMTP de produção — ver mensagem já escrita
  pro cliente (`tasks/10-deploy.md`, seção de pendências).

## Fora desta fase
- Pagamento online (Stripe/PayPal) — item avulso, +€400/+1-2 semanas, não decidido.
