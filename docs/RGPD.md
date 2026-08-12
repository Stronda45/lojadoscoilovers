# RGPD — implementação técnica (Fase 2)

Escopo contratado (`proposta-v2-intermediario.pdf`): coleta mínima, consentimento no
cadastro, exclusão de conta. A política de privacidade em si é responsabilidade do
cliente — aqui é só a parte técnica.

## Coleta mínima — já cumprido
`Customer` (`core/models.py`) só guarda nome (no `User`), e-mail, telefone, endereço
de entrega — exatamente o que o cliente confirmou que precisa
(`questionario.txt`, 3.2). Nada a mudar no schema por causa disso.

## Consentimento no cadastro
- `Customer.consent_accepted_at` (DateTimeField, null=True) — timestamp de quando o
  cliente final aceitou os termos. Guardar timestamp, não só um booleano, pra ter
  registro de *quando* (útil se os termos mudarem).
- `RegisterSerializer` (`core/serializers.py`) exige um campo `accepts_terms`
  (booleano, `required=True`) — se `False`, rejeita o cadastro com erro de validação
  (não silenciosamente ignora).
- `RegisterPage.jsx` (frontend): checkbox obrigatório antes do botão "Criar conta",
  com link pra política de privacidade (URL do cliente — pendente, ver Fase 2 draft
  da mensagem ao cliente).

## Exclusão de conta — anonimizar, não apagar

**Decisão**: `Order` tem `on_delete=models.PROTECT` pro `Customer`
(`core/models.py`) — ou seja, hoje já **não é possível** apagar um `Customer` com
pedidos sem quebrar a integridade referencial. Em vez de mudar isso pra
`CASCADE` (que apagaria histórico de pedido — ruim pro cliente/dono, que pode
precisar disso pra contabilidade ou disputa com o fornecedor), a exclusão
**anonimiza**:

1. Apaga o `User` (login) — ou marca `is_active=False` + limpa `email`/`username`
   pra um valor não-reversível (ex: `deleted-user-<id>@anon.local`).
2. `Customer.phone` e `Customer.delivery_address` substituídos por placeholder
   (`"[dado removido]"`).
3. Token de autenticação (`rest_framework.authtoken`) apagado — sessão morre na
   hora.
4. `Order`/`OrderItem` **permanecem intactos** — o pedido histórico (o que foi
   comprado, quando, por quanto) não é dado pessoal identificável depois do passo 2/3.

Endpoint: `DELETE /auth/me` (autenticado — usuário só apaga a própria conta).
Frontend: botão "Excluir minha conta" numa área de conta (nova tela, ou dentro de
`OrdersPage.jsx`) com confirmação (não é um clique só — ação irreversível).

## O que isso NÃO cobre (fora do escopo contratado)
- Exportação de dados pessoais (direito de portabilidade) — não estava no PDF, não
  entra a menos que o cliente peça e isso vire item avulso.
- Cookie consent banner no frontend — RGPD de cookies é diferente de RGPD de dados
  de cadastro; não mencionado na proposta, não assumir que está incluso.
