# Import de Excel/CSV de outros fornecedores — Fase 2

**Status: bloqueada.** Não estava no escopo original da Fase 2 (`proposta-v2-
intermediario.pdf`) — surgiu numa conversa à parte com o cliente. Antes de
implementar, precisa: (a) alinhar com o cliente se entra nos €1.200 ou é cobrado à
parte, (b) respostas da seção 7 de `perguntas-para-cliente.txt`.

Este doc registra o que já sabemos pelos arquivos reais (`csvs.rar`, mandado pelo
cliente, inspecionado em 2026-08-12) — pra quando a implementação começar, o desenho
já estar pronto.

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

## Mecanismo de import — recomendação: comando, não upload no browser

A ideia original (`docs/FASE2-NOTAS.md`) era um wizard no browser com mapeamento de
colunas — fazia sentido quando os formatos eram hipotéticos/desconhecidos. Agora que
temos os 4 arquivos reais e conhecemos os formatos exatos, **um upload+mapeamento
genérico no browser é trabalho maior do que o problema exige**, e nem é prático:
o arquivo master da MTS tem 206MB — upload direto pelo navegador arrisca timeout,
e processar 206 mil linhas dentro de uma request HTTP não é viável (sem fila de
job/worker, que não existe no projeto hoje e adicionar é infraestrutura nova).

**Recomendação**: parser dedicado por fornecedor (4 funções conhecidas, não um
mapeamento genérico) rodado via **management command** do Django
(`python manage.py import_supplier <nome> <caminho-do-arquivo>`), executado por
quem tiver acesso ao servidor (você ou, futuramente, o cliente via instrução simples)
sempre que uma planilha nova chegar. Processa em streaming (não carrega o arquivo
inteiro em memória) e usa `bulk_create`/`bulk_update` em lote.

Isso é mais barato de construir e testar (bate com "testes automatizados mínimos" do
orçamento da Fase 2) do que uma UI de upload self-service completa. Se o cliente
quiser mesmo assim fazer upload sozinho pelo navegador no futuro, isso vira um item
avulso — não é a mesma conta de "importar 4 planilhas conhecidas".

## Busca dos produtos importados

Catálogo separado da busca do dtsshop.de (decisão já tomada — sem cascata de
veículo compartilhada). Duas variantes possíveis dependendo da resposta à pergunta
7.4:
- **Com fitment** (usa `ImportedProductFitment`): cascata marca→modelo própria,
  igual em espírito à do dtsshop.de mas mais simples (dado já vem estruturado, sem
  Playwright/scraping — é só uma query no banco).
- **Sem fitment** (fallback se o cliente preferir simples): busca por texto/
  categoria direto em `ImportedProduct`, ignora `ImportedProductFitment`.

## Pendências (ver `perguntas-para-cliente.txt`, seção 7)
- Importar só o master da MTS, só os recortes por categoria, ou os dois?
- Margem aplica sobre `Netto EK` (custo) da TA Technix, ou usa o `UVP` dele direto?
- Como precificar as rodas (sem preço no arquivo)?
- Busca com cascata de veículo ou simples (texto/categoria)?
- Fotos das rodas vieram vazias — tem em outro lugar?
- Frequência de atualização dos arquivos.
