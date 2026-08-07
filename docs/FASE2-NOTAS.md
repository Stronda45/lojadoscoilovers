# Notas pré-planejamento — Fase 2

Decisões e pendências levantadas antes da Fase 2 começar oficialmente (sem
tasks/ ainda — isso vira tasks quando a Fase 2 for iniciada). Serve pra não
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
