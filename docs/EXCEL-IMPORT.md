# Import de Excel/CSV de outros fornecedores — Fase 2

**Status: parcialmente implementada** (2026-08-12) — models, parsers dos 4
fornecedores, upload com segurança e upsert já funcionam, testados contra os
arquivos reais. Não estava no escopo original da Fase 2 (`proposta-v2-
intermediario.pdf`) — surgiu numa conversa à parte com o cliente. Falta pra
fechar: (a) alinhar com o cliente se entra nos €1.200 ou é cobrado à parte,
(b) respostas da seção 7 de `perguntas-para-cliente.txt`, (c) tela de busca
no frontend. Ver `tasks/fase2/04-import-excel-csv.md` pro detalhe do que já
foi feito vs. pendente.

## Os 4 fornecedores são muito diferentes entre si

| Fornecedor | Formato | Linhas | Compatibilidade de carro | Preço |
|---|---|---|---|---|
| MTS | 6 CSVs (1 master + 5 por categoria) | 206 mil (master) | **Sim** — make/model/series/engine/year por linha | `msrp` (1 valor) |
| TA Technix | 1 CSV | ~10.500 | **Sim** — Hersteller/Modell/Typ/Baujahr por linha | **2 valores**: `Netto EK` (custo) e `UVP` (venda sugerida) |
| Cheney (rodas) | 1 XLSX | — | Não — compatibilidade por medida (PCD/ET/CB), não por veículo | **Nenhum** |
| ES2WHEELS (rodas) | 1 XLSX | — | Não — mesma lógica de rodas | **Nenhum** |

Isso **não é "planilha de preço simples"** — MTS e TA Technix têm fitment completo,
no mesmo nível do dtsshop.de (uma linha por combinação peça×motorização). As rodas
são mais simples estruturalmente mas não têm preço, então não dá pra vender "clique
e compre" sem resolver isso com o cliente primeiro (pergunta 7.3).

## Desenho de dados proposto

Um schema genérico o suficiente pra cobrir os 4 formatos sem tabela por fornecedor:

```python
class Supplier(models.Model):
    name = models.CharField(...)  # "MTS", "TA Technix", "Cheney", "ES2WHEELS"
    selected_fields = models.JSONField(default=list, blank=True)
    # lista dos nomes de campo (de raw_attributes) que o cliente escolheu
    # importar/exibir pra esse fornecedor — ver seção "Cliente escolhe as colunas"

class ImportedProduct(models.Model):
    supplier = models.ForeignKey(Supplier, ...)
    external_reference = models.CharField(...)  # part_number / Artikelnummer / MODEL
    title = models.CharField(...)
    description = models.TextField(blank=True)
    cost_price = models.DecimalField(null=True, blank=True)  # null pras rodas (sem preço ainda)
    image_url = models.URLField(blank=True)
    category = models.CharField(blank=True)
    raw_attributes = models.JSONField(default=dict)  # campos específicos do fornecedor
    active = models.BooleanField(default=True)  # false se sumiu do arquivo mais recente
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["supplier", "external_reference"]  # chave de dedupe/update

class ImportedProductFitment(models.Model):
    product = models.ForeignKey(ImportedProduct, related_name="fitments", ...)
    make = models.CharField(...)
    model = models.CharField(...)
    variant = models.CharField(blank=True)  # engine/Typ
    year_range = models.CharField(blank=True)
```

`raw_attributes` (JSON) guarda o que só existe num fornecedor específico — ex:
`body_type`/`drive_type`/`fuel_type` (MTS), `PCD`/`ET`/`CB`/`FINISH`/`STOCK`
(rodas) — sem precisar de tabela nova a cada formato diferente.

`ImportedProduct` é deduplicado por `(supplier, external_reference)` — MTS e TA
Technix repetem a mesma peça em várias linhas (uma por veículo compatível); isso vira
1 `ImportedProduct` + N `ImportedProductFitment`, não N produtos.

**Preço de venda**: mesma função `apply_margin()` já existente (`core/models.py`) —
reusa a regra de margem/faixa de preço, não inventa uma nova.

## Mecanismo de import — upload self-service pelo cliente (decisão 2026-08-12)

**Decisão revista**: o cliente vai poder subir os arquivos ele mesmo, sempre que
precisar (não depende de comando rodado por nós). Parser continua **dedicado por
fornecedor** (4 funções conhecidas, não um mapeamento genérico de colunas — os
formatos já são conhecidos, isso não muda).

**Implementado dentro do Django Admin**, não como endpoint de API separado —
`ImportedProductAdmin.upload_view` (`core/admin.py`), sessão do admin, não token.
Pensamos primeiro num endpoint DRF (`POST /catalog/upload` com `IsAdminUser`), mas
isso não bate com a decisão da task 02 (painel = Django Admin, dono/funcionário
autenticam por sessão, não têm/usam token de API) — corrigido antes de ir pra
produção. `GET /catalog/search` continua como endpoint DRF público de verdade
(consumido pelo frontend, como o `/search` do dtsshop.de).

### O limite real: o arquivo master da MTS (206MB)

Processar 206 mil linhas dentro de uma requisição HTTP não é viável sem fila de
job/worker (infraestrutura que o projeto não tem hoje — adicionar é custo/
complexidade novos, mais hospedagem). Os outros arquivos (TA Technix ~10,5k linhas,
rodas, e os recortes por categoria da MTS — 1,2k a 85k linhas) processam numa
requisição normal, de forma eficiente (streaming, sem carregar tudo em memória).

**Caminho padrão**: cliente sobe os arquivos por categoria da MTS, não o master —
funciona com a infraestrutura atual, sem custo extra.

**Se o cliente quiser mesmo assim o master de 206MB de uma vez**: é tecnicamente
possível, mas exige fila de job (Celery/Redis ou alternativa mais leve como
`django-rq`/`huey`) — infraestrutura nova, mais hospedagem, mais escopo. **Vira
item cobrado à parte**, não incluso na Fase 2 — precisa ser explícito com o cliente
antes, não assumido.

### Documentação pro cliente (não-técnico)

Precisa de um guia curto (passo a passo, sem jargão) cobrindo:
1. Onde fazer o upload (tela do admin).
2. **Por que usar os arquivos por categoria da MTS, não o master** — explicar em
   termos simples (arquivo muito grande, sistema não processa de uma vez sem custo
   extra de servidor) pra ele entender a razão, não só a regra.
3. O que esperar depois de subir (produto atualizado x novo, tempo de
   processamento).
4. O que fazer se der erro (mensagem de erro amigável, não stack trace).

Fica como entregável desta task, não é opcional — sem isso, o cliente não-técnico
não usa a feature sozinho, que era o objetivo.

## Segurança do upload (obrigatório, não opcional)

Upload self-service de arquivo é superfície de ataque — checklist a implementar:

- **Validar extensão E conteúdo real** do arquivo (não confiar só no nome — dá pra
  renomear qualquer arquivo pra `.csv`). Verificar assinatura/estrutura real antes
  de processar.
- **Limite de tamanho** no upload — rejeita antes de processar, evita esgotar
  memória/disco de propósito.
- **Zip bomb**: TA Technix já vem num zip — limitar tamanho descomprimido, não só o
  tamanho do arquivo enviado (um zip pequeno pode descomprimir pra gigabytes).
- **Path traversal** ao descompactar — usar `zipfile`/`openpyxl` do Python
  diretamente, nunca chamar `unzip`/`unrar` via shell com nome de arquivo vindo do
  usuário interpolado na string do comando (evita injeção de comando de vez, não só
  mitiga).
- **CSV injection**: célula começando com `=`, `+`, `-`, `@` pode virar fórmula se
  alguém reabrir o dado num Excel depois (ex: exportar um relatório) — escapar esses
  valores ao guardar.
- **Só aceitar `.xlsx`/`.csv`**, nunca `.xlsm` (macro) — `openpyxl` não executa
  macro, mas não precisamos nem correr esse risco.
- SQL injection não é vetor aqui — tudo passa pelo Django ORM (parametrizado), sem
  SQL bruto montado com dado do arquivo.

## Cliente escolhe quais colunas importam (decisão 2026-08-12)

Cada fornecedor tem dezenas de colunas (`raw_attributes`) — nem todas interessam pro
cliente mostrar na loja. Em vez de um mapeamento genérico ("qual coluna é qual
campo", já resolvido pelos parsers dedicados), a escolha aqui é mais simples:
**quais dos campos já extraídos aparecem** — uma lista editável por fornecedor
(`Supplier.selected_fields`, ver schema acima), configurável no admin. Reduz
retrabalho (cliente ajusta sem pedir mudança de código) sem precisar construir uma
tela de mapeamento completa.

## Busca dos produtos importados — implementada (2026-08-12)

Catálogo separado da busca do dtsshop.de (sem cascata de veículo compartilhada).
Cliente respondeu a pergunta 7.4: quer os **dois tipos de busca**, texto e
veículo, combináveis.

- `GET /catalog/makes` — marcas com fitment cadastrado (MTS/TA Technix; rodas
  não aparecem aqui, não têm fitment).
- `GET /catalog/makes/<make>/models` — modelos daquela marca.
- `GET /catalog/variants?make=&model=` — motorizações daquele modelo.
- `GET /catalog/search?make=&model=&variant=&q=&category=` — todos os
  parâmetros são opcionais e combináveis; produto sem fitment (rodas) só
  aparece via `q`/`category`, nunca via `make`/`model`/`variant`.

Cascata é só query no banco (`ImportedProductFitment`), sem Playwright/scraping —
mais simples que a do dtsshop.de porque o dado já vem estruturado do arquivo.
7 testes automatizados cobrindo isso em `core/tests_importers.py`.

## Achados testando contra os arquivos reais (não amostras)

- **MTS usa vírgula decimal** ("707,25", "699"), não ponto como parecia pelo
  primeiro exemplo inspecionado — corrigido pra usar o mesmo parser europeu
  da TA Technix.
- **TA Technix "Hersteller" nem sempre é 1 marca limpa**: pode ter várias
  ("passend für Audi / Seat / VW") ou ser lixo/peça universal ("Universell",
  "1 Set") — tratado como 0-N fitments, não erro de parsing.
- **Rodas não têm coluna de SKU** — referência construída a partir de
  modelo+medida+furação+offset+acabamento.
- **Desativação por fornecedor inteiro estava errada**: a MTS manda 1
  arquivo por categoria — sem escopar a desativação por categoria, importar
  o 2º arquivo apagava (desativava) o 1º. Corrigido, coberto por teste de
  regressão.
- **Gap de permissão no upload**: `admin_view()` do Django só garante
  `is_staff`, não checa permissão de model pra URLs customizadas — um
  funcionário sem permissão em `ImportedProduct` conseguia acessar a página
  de upload só adivinhando a URL. Fechado com checagem explícita de
  `has_add_permission`.

63 testes automatizados (32 da task 03 + 31 novos) cobrem os pontos acima —
`backend/core/tests_importers.py`.

## Pendências (ver `perguntas-para-cliente.txt`, seção 7)
- Importar só o master da MTS, só os recortes por categoria, ou os dois? (Se
  master: confirmar que ele topa o custo extra de infraestrutura — item à parte.)
- Margem aplica sobre `Netto EK` (custo) da TA Technix, ou usa o `UVP` dele direto?
- Como precificar as rodas (sem preço no arquivo)?
- Busca com cascata de veículo ou simples (texto/categoria)?
- Fotos das rodas vieram vazias — tem em outro lugar?
- Frequência de atualização dos arquivos.
