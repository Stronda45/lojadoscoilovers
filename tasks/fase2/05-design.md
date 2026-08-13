# 05 — Design de verdade (identidade visual)

**Status: em andamento.** Nome, logo e direção de cor recebidos e aplicados
(2026-08-12, `conversa.md`). Falta: banner (foto ainda é placeholder Pexels —
cliente não mandou substituto, não bloqueia), revisão geral de
tipografia/espaçamento, e decisão sobre renomear o repositório/pasta do
projeto (`questionario.txt`, 5.1, ainda não feito — é operacional, não
puramente visual, ver nota abaixo).

## Contexto
Contratado: "design de verdade na interface (identidade visual da sua marca)."
Fase 1 já tinha uma base funcional com acabamento mínimo (header, cards, banner com
foto placeholder — ver `tasks/08-frontend-busca.md`, `docs/FRONTEND.md`) que serviu
de esqueleto pra aplicar a identidade real por cima.

## Recebido do cliente (2026-08-12)
- **Nome**: Loja dos Coilovers.
- **Logo**: `imgs/WhatsApp Image 2026-08-12 at 14.58.05.jpeg` (mola vermelha +
  amortecedor preto, tipografia branca/preta, fundo preto) —
  `frontend/public/logo.jpg`.
- **Cores**: "as presentes no logo, mas não muito preto — mais branco/cinza,
  com detalhes a preto e vermelho."

## Tarefas
- [x] Logo real aplicado no header (`App.jsx`), substituindo o SVG genérico.
- [x] Nome "Loja dos Coilovers" em `index.html` (title), header e favicon.
- [x] Paleta revisada (`index.css`): fundo/superfícies continuam
      branco/cinza claro (já eram); topo (header) e faixa do banner viraram
      **preto** (`--ink`/`--ink-dark`, gradiente); vermelho da marca
      (`--primary: #d21f1f`) virou a cor de destaque — preço, botões
      principais ("Pedir"), links de ação, borda de 3px entre header/hero e
      o resto da página.
- [ ] Banner da home continua com a foto Pexels placeholder da Fase 1 — não
      trocado (cliente não mandou substituto nem pediu explicitamente pra
      trocar essa foto especificamente, só a paleta de cor geral).
- [ ] Revisão geral de tipografia/espaçamento com o resultado real do uso.
- [ ] **Nome do repositório/pasta** (`lojadoscoilovers` → algo com "Loja dos
      Coilovers"?) — cliente mencionou isso no questionário original
      (5.1), mas é uma mudança operacional (git remote, deploy, URLs), não
      só visual. Não fizemos ainda — decidir junto com o deploy (task 10),
      não no meio do desenvolvimento.

## Aceite
- [x] Header/hero testados ao vivo (Playwright dirigindo o frontend real) —
      logo, nome e cores aplicados sem erro de console.
- [ ] Interface 100% sem asset placeholder ainda pendente (banner).

## Arquivos
`frontend/public/logo.jpg` (novo), `frontend/index.html`, `frontend/src/App.jsx`,
`frontend/src/index.css`. `frontend/src/components/Logo.jsx` removido (SVG
genérico não usado mais).
