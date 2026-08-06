# Fase 1 — Backend funcional + UI mínima

Prazo: 2 semanas a partir da aprovação. €800. Sem design, sem RGPD, sem testes
automatizados (isso é Fase 2). Foco: sistema funcionando ponta a ponta.

## Ordem de execução

| # | Tarefa | Estimativa | Bloqueada por |
|---|--------|-----------|---------------|
| 01 | Scaffold Django + DRF | 3h | - |
| 02 | Conector dtsshop.de — dados JSON (veículo/categoria/preço-estoque) | 8h | 01 |
| 03 | Conector dtsshop.de — HTML (listagem de produtos/busca) | 10h | 01 |
| 04 | Models: Customer, Order, regra de margem | 5h | 01 |
| 05 | Auth (cadastro/login) | 4h | 04 |
| 06 | Fluxo de pedido (backend) | 4h | 02, 03, 04 |
| 07 | Alerta por e-mail em novo pedido | 3h | 06 |
| 08 | Frontend — busca e resultados (sem design) | 5h | 02, 03 |
| 09 | Frontend — login/cadastro/pedido (sem design) | 5h | 05, 06 |
| 10 | Deploy (Vercel + Railway) | 3h | 08, 09 |

**Total: ~50h** (orçado 45-50h — 2 semanas a 20h/semana é justo, sem folga).

## Pendências que bloqueiam início real (não bloqueiam preparar o código)

- **Regra de margem**: cliente disse "1.30 do preço" — não confirmado se é 1,30×
  (+30%) ou 1,30% (+0,013×). Task 04 implementa como **configurável** (valor fixo OU
  multiplicador) justamente por causa dessa incerteza — não trava o código, só o
  valor default até ele confirmar.
- **Nome/domínio**: usando `lojadoscoilovers` como nome de trabalho — ver
  `file.md` (raiz do famaInPecas) para status.

## Fora desta fase (não criar tarefa ainda)

- RGPD (código), painel admin, testes automatizados, design — Fase 2.
- Import de Excel de outros fornecedores — Fase 2.
- Pagamento online — item avulso, não decidido.
