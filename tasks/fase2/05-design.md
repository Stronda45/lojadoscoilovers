# 05 — Design de verdade (identidade visual)

**Status: bloqueada.** Bloqueada por: nome final da marca, logo, paleta de cores —
nenhum recebido ainda (`questionario.txt`, 5.1: marca já existe mas o nome vai
mudar; sem assets visuais até agora).

## Contexto
Contratado: "design de verdade na interface (identidade visual da sua marca)."
Fase 1 já tem uma base funcional com acabamento mínimo (header, cards, banner com
foto placeholder — ver `tasks/08-frontend-busca.md`, `docs/FRONTEND.md`) que serve
de esqueleto pra aplicar a identidade real por cima, não é do zero.

## Objetivo
Interface com a cara da marca do cliente, não mais o placeholder genérico da Fase 1.

## Tarefas (a detalhar quando destravar)
- [ ] Receber do cliente: nome final, logo (SVG/PNG), paleta de cores, referências
      visuais (se tiver).
- [ ] Trocar `Logo.jsx` (SVG genérico) pelo logo real.
- [ ] Trocar `hero-car.jpg` (foto Pexels placeholder) por asset da marca, se o
      cliente quiser algo diferente.
- [ ] Revisar paleta em `index.css` (`--primary`/`--primary-dark` hoje são um azul
      genérico escolhido por nós).
- [ ] Revisão geral de tipografia/espaçamento com o resultado real do uso da Fase 1
      (itens que incomodaram na prática).

## Aceite
- [ ] Interface não usa mais nenhum asset placeholder (SVG genérico, foto Pexels,
      cores escolhidas por nós sem input do cliente).

## Arquivos
`frontend/src/components/Logo.jsx`, `frontend/src/components/Hero.jsx`,
`frontend/src/index.css`, `frontend/public/hero-car.jpg`.
