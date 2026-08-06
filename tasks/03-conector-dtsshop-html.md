# 03 — Conector dtsshop.de: HTML (listagem de produtos/busca)

Estimativa: 10h · Bloqueada por: 01

## Objetivo
Implementar a parte do conector que precisa interpretar HTML renderizado (confirmado
ao vivo: não existe endpoint JSON pra isso).

## Tarefas
- [ ] `list_products(category_id, car_id)` — busca `/shop?pgs=[...]` com veículo
      selecionado, extrai nome/imagem/`product_id` de cada item.
- [ ] `search(query)` — busca a página de resultados de busca, mesmos campos.
- [ ] Combinar com task 02: depois de listar `product_id`s, chamar
      `get_price_and_availability` pra completar preço/estoque.
- [ ] Isolar seletores CSS num módulo único (facilita manutenção se o tema mudar).
- [ ] Erro controlado se o HTML mudar de estrutura (não crash silencioso).

## Aceite
- [ ] `list_products` retorna itens reais com nome/imagem/preço/estoque.
- [ ] `search` retorna resultados reais.
- [ ] Mudança de estrutura no HTML produz erro claro, não dado errado.
