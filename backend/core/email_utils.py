"""Envio de e-mail assincrono (thread), mesmo padrao usado em outros projetos
do freela (envio nao trava a resposta HTTP, retry em erro intermitente de rede)."""

import logging
import threading
import time

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db import connection
from django.utils.html import format_html, format_html_join

logger = logging.getLogger(__name__)


def _send_email_safe(
    subject: str,
    body_plain: str,
    body_html: str | None,
    to_emails: list[str] | str,
) -> bool:
    if getattr(settings, "EMAIL_DISABLE_OUTBOUND", False):
        logger.info(f"[email] outbound desabilitado — não enviaria '{subject}' para {to_emails}")
        return True

    if isinstance(to_emails, str):
        to_emails = [to_emails]
    if not to_emails:
        logger.warning(f"[email] '{subject}' sem destinatário — não enviado.")
        return False

    def send_action():
        max_retries = 3
        for attempt in range(max_retries):
            try:
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=body_plain,
                    from_email=settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER,
                    to=to_emails,
                )
                if body_html:
                    email.attach_alternative(body_html, "text/html")
                email.send(fail_silently=False)
                logger.info(f"E-mail '{subject}' enviado para {to_emails} (tentativa {attempt + 1})")
                break
            except Exception as e:
                is_last = attempt == max_retries - 1
                if is_last:
                    logger.error(f"Falha ao enviar '{subject}' após {max_retries} tentativas: {e}", exc_info=True)
                else:
                    logger.warning(f"Erro ao enviar '{subject}' (tentativa {attempt + 1}): {e}. Tentando de novo em 2s.")
                    time.sleep(2)
            finally:
                connection.close()

    threading.Thread(target=send_action).start()
    return True


def send_new_order_alert_email(order) -> bool:
    """Avisa a equipe (`settings.TEAM_ALERT_EMAILS`) que um pedido novo chegou —
    quanto mais rápido comprarem no fornecedor, menor o risco de o estoque
    esgotar antes da compra."""
    customer = order.customer
    subject = f"Novo pedido #{order.pk} — comprar no fornecedor"

    lines = []
    for item in order.items.all():
        lines.append(
            f"- {item.product_name} (id fornecedor: {item.supplier_product_id}) "
            f"x{item.quantity} — custo €{item.cost_price} / venda €{item.sale_price}"
        )
    items_plain = "\n".join(lines)
    items_html = format_html_join(
        "",
        "<li>{} (id fornecedor: {}) x{} — custo €{} / venda €{}</li>",
        (
            (item.product_name, item.supplier_product_id, item.quantity, item.cost_price, item.sale_price)
            for item in order.items.all()
        ),
    )

    customer_name = customer.user.get_full_name() or customer.user.username

    body_plain = f"""Pedido #{order.pk} recebido.

Cliente: {customer_name}
E-mail: {customer.user.email}
Telefone: {customer.phone}
Endereço de entrega: {customer.delivery_address}

Itens:
{items_plain}

Confirme preço/estoque no dtsshop.de (buscar pelo id do fornecedor listado
acima) antes de comprar — disponibilidade não é garantida até a compra.
"""

    body_html = format_html(
        '<div style="font-family: Arial, sans-serif; font-size: 14px; color: #222;">'
        "<h2>Pedido #{} recebido</h2>"
        "<p><strong>Cliente:</strong> {}<br/>"
        "<strong>E-mail:</strong> {}<br/>"
        "<strong>Telefone:</strong> {}<br/>"
        "<strong>Endereço de entrega:</strong> {}</p>"
        "<p><strong>Itens:</strong></p>"
        "<ul>{}</ul>"
        "<p>Confirme preço/estoque no dtsshop.de (buscar pelo id do fornecedor "
        "listado acima) antes de comprar — disponibilidade não é garantida "
        "até a compra.</p>"
        "</div>",
        order.pk,
        customer_name,
        customer.user.email,
        customer.phone,
        customer.delivery_address,
        items_html,
    )

    return _send_email_safe(subject, body_plain, body_html, settings.TEAM_ALERT_EMAILS)
