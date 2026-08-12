# Notas pré-planejamento — Fase 2 (histórico)

**Superado por `tasks/fase2/` e `docs/EXCEL-IMPORT.md`/`docs/RGPD.md`** (2026-08-12)
— este arquivo fica como registro do raciocínio inicial, antes de termos os
arquivos reais do cliente. A abordagem de "importador com mapeamento de colunas"
descrita abaixo foi **revista**: com os arquivos reais em mãos, os formatos já são
conhecidos (não precisam ser descobertos via mapeamento genérico) — ver
`docs/EXCEL-IMPORT.md` pro desenho atual.

Decisões e pendências levantadas antes da Fase 2 começar oficialmente. Serve pra não
perder o contexto entre agora e lá.

## Import de Excel/CSV de outros fornecedores

Cliente tem produtos de outros fornecedores em planilhas, formatos não
necessariamente iguais entre eles.

**Abordagem decidida**: importador com mapeamento de colunas (não um
template fixo obrigatório). Cliente sobe o arquivo como está; a tela mostra
as colunas encontradas e ele mapeia pra que campo cada uma corresponde
("Coluna B = preço", "Coluna D = estoque"). Motivo: aguenta formato diferente
por fornecedor sem exigir que ele reformate nada.

- [x] Template de referência (exemplo do formato ideal) — construímos nós
      mesmos, não depende do cliente. Serve de apoio/exemplo, não é
      obrigatório pro cliente seguir à risca (o mapeamento cobre desvios).
- [x] Upload é **recorrente**, sem periodicidade fixa — cliente disse "estou
      sempre colocando". **Implica**: precisa de tela de upload no painel
      admin (Fase 2, não script único), e lógica de update/dedupe (produto já
      existente atualiza preço/estoque, não duplica) — não é só criação.
- [ ] **Pendente do cliente**: quais colunas importam pro negócio (nome, nº
      peça, marca, preço, estoque, compatibilidade de carro?).
- [ ] **Pendente do cliente**: preço nas planilhas vem com ou sem imposto?

## Outros itens já sabidos como Fase 2 (sem detalhamento ainda)
RGPD (implementação), painel admin, testes automatizados, design de UI — ver
`tasks/00-overview.md` (seção "Fora desta fase").
