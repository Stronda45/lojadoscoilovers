"""Testes automatizados mínimos do módulo mais frágil do sistema (conector
dtsshop.de) — Fase 2, task 03. Tudo mockado (requests/Playwright), nada toca
a rede de verdade. Cobre o caminho feliz + SupplierError em falha de rede/
formato inesperado, pra cada função pública do conector, e 2 regressões de
bugs já corrigidos em produção."""

from decimal import Decimal
from unittest.mock import MagicMock, patch

import requests
from django.test import TestCase

from core.connectors import dtsshop
from core.connectors.dtsshop import SupplierError
from core.models import PriceTablePoint, apply_margin
from core.search_views import _enrich_with_price


def _mock_response(json_data=None, text="", raise_for_status_exc=None, json_exc=None):
    resp = MagicMock()
    if raise_for_status_exc:
        resp.raise_for_status.side_effect = raise_for_status_exc
    else:
        resp.raise_for_status.return_value = None
    resp.text = text
    if json_exc:
        resp.json.side_effect = json_exc
    else:
        resp.json.return_value = json_data
    return resp


class GetCarDataTests(TestCase):
    @patch("core.connectors.dtsshop.requests.get")
    def test_caminho_feliz(self, mock_get):
        mock_get.return_value = _mock_response(json_data={"makes": [{"id": "5", "name": "AUDI"}]})
        result = dtsshop.get_car_data()
        self.assertEqual(result, {"makes": [{"id": "5", "name": "AUDI"}]})

    @patch("core.connectors.dtsshop.requests.get")
    def test_falha_de_rede_vira_supplier_error(self, mock_get):
        mock_get.side_effect = requests.ConnectionError("host inexistente")
        with self.assertRaises(SupplierError):
            dtsshop.get_car_data()

    @patch("core.connectors.dtsshop.requests.get")
    def test_json_invalido_vira_supplier_error(self, mock_get):
        mock_get.return_value = _mock_response(json_exc=ValueError("not json"))
        with self.assertRaises(SupplierError):
            dtsshop.get_car_data()


class GetModelsTests(TestCase):
    @patch("core.connectors.dtsshop.requests.get")
    def test_caminho_feliz(self, mock_get):
        mock_get.return_value = _mock_response(json_data=[{"id": "4955", "name": "A3 (8P)"}])
        result = dtsshop.get_models("5")
        self.assertEqual(result, [{"id": "4955", "name": "A3 (8P)"}])

    @patch("core.connectors.dtsshop.requests.get")
    def test_falha_de_rede_vira_supplier_error(self, mock_get):
        mock_get.side_effect = requests.Timeout("demorou demais")
        with self.assertRaises(SupplierError):
            dtsshop.get_models("5")


class GetCarsTests(TestCase):
    @patch("core.connectors.dtsshop.requests.get")
    def test_caminho_feliz(self, mock_get):
        mock_get.return_value = _mock_response(json_data=[{"id": "33251", "name": "1.2 TSI"}])
        result = dtsshop.get_cars("5", "4955")
        self.assertEqual(result, [{"id": "33251", "name": "1.2 TSI"}])

    @patch("core.connectors.dtsshop.requests.get")
    def test_falha_de_rede_vira_supplier_error(self, mock_get):
        mock_get.side_effect = requests.ConnectionError()
        with self.assertRaises(SupplierError):
            dtsshop.get_cars("5", "4955")


class GetCategoriesTests(TestCase):
    @patch("core.connectors.dtsshop.requests.get")
    def test_caminho_feliz(self, mock_get):
        mock_get.return_value = _mock_response(json_data=[{"id": 26, "name": "Suspensions"}])
        result = dtsshop.get_categories("33251")
        self.assertEqual(result, [{"id": 26, "name": "Suspensions"}])

    @patch("core.connectors.dtsshop.requests.get")
    def test_falha_de_rede_vira_supplier_error(self, mock_get):
        mock_get.side_effect = requests.ConnectionError()
        with self.assertRaises(SupplierError):
            dtsshop.get_categories("33251")


class SessionWithFormKeyTests(TestCase):
    @patch("core.connectors.dtsshop.requests.Session")
    def test_extrai_form_key_da_home(self, mock_session_cls):
        mock_session = MagicMock()
        mock_session.get.return_value = _mock_response(
            text='<input name="form_key" type="hidden" value="abc123" />'
        )
        mock_session_cls.return_value = mock_session

        session, form_key = dtsshop._session_with_form_key()
        self.assertEqual(form_key, "abc123")
        self.assertIs(session, mock_session)

    @patch("core.connectors.dtsshop.requests.Session")
    def test_form_key_nao_encontrado_vira_supplier_error(self, mock_session_cls):
        mock_session = MagicMock()
        mock_session.get.return_value = _mock_response(text="<html>sem form_key aqui</html>")
        mock_session_cls.return_value = mock_session

        with self.assertRaises(SupplierError):
            dtsshop._session_with_form_key()

    @patch("core.connectors.dtsshop.requests.Session")
    def test_falha_de_rede_vira_supplier_error(self, mock_session_cls):
        mock_session = MagicMock()
        mock_session.get.side_effect = requests.ConnectionError()
        mock_session_cls.return_value = mock_session

        with self.assertRaises(SupplierError):
            dtsshop._session_with_form_key()


class GetPriceAndAvailabilityTests(TestCase):
    def test_lista_vazia_nao_faz_request(self):
        self.assertEqual(dtsshop.get_price_and_availability([]), {})

    @patch("core.connectors.dtsshop._session_with_form_key")
    def test_achata_resposta_lista_de_dicts_de_1_chave(self, mock_session_form_key):
        mock_session = MagicMock()
        mock_session.post.return_value = _mock_response(
            json_data=[
                {"123": {"price": "9.70", "availability": {"text": "In stock"}}},
                {"456": {"price": "15.00", "availability": {"text": "ships in 2 days"}}},
            ]
        )
        mock_session_form_key.return_value = (mock_session, "formkey123")

        result = dtsshop.get_price_and_availability(["123", "456"])
        self.assertEqual(result["123"]["price"], "9.70")
        self.assertEqual(result["456"]["price"], "15.00")

    @patch("core.connectors.dtsshop._session_with_form_key")
    def test_falha_de_rede_vira_supplier_error(self, mock_session_form_key):
        mock_session = MagicMock()
        mock_session.post.side_effect = requests.ConnectionError()
        mock_session_form_key.return_value = (mock_session, "formkey123")

        with self.assertRaises(SupplierError):
            dtsshop.get_price_and_availability(["123"])

    @patch("core.connectors.dtsshop._session_with_form_key")
    def test_json_invalido_vira_supplier_error(self, mock_session_form_key):
        mock_session = MagicMock()
        mock_session.post.return_value = _mock_response(json_exc=ValueError("not json"))
        mock_session_form_key.return_value = (mock_session, "formkey123")

        with self.assertRaises(SupplierError):
            dtsshop.get_price_and_availability(["123"])


class ExtractProductsViaBrowserTests(TestCase):
    def _mock_playwright(self, evaluate_return):
        mock_page = MagicMock()
        mock_page.evaluate.return_value = evaluate_return
        mock_context = MagicMock()
        mock_context.new_page.return_value = mock_page
        mock_browser = MagicMock()
        mock_browser.new_context.return_value = mock_context
        mock_p = MagicMock()
        mock_p.chromium.launch.return_value = mock_browser
        mock_cm = MagicMock()
        mock_cm.__enter__.return_value = mock_p
        mock_cm.__exit__.return_value = False
        return mock_cm, mock_context

    @patch("core.connectors.dtsshop.sync_playwright")
    def test_caminho_feliz_devolve_groups(self, mock_sync_playwright):
        groups = [{"group_name": "Coilover", "products": [{"id": 1}]}]
        mock_cm, _ = self._mock_playwright(groups)
        mock_sync_playwright.return_value = mock_cm

        result = dtsshop._extract_products_via_browser("https://example.test", None)
        self.assertEqual(result, groups)

    @patch("core.connectors.dtsshop.sync_playwright")
    def test_seta_cookies_de_carro_quando_fornecidos(self, mock_sync_playwright):
        mock_cm, mock_context = self._mock_playwright([])
        mock_sync_playwright.return_value = mock_cm

        dtsshop._extract_products_via_browser(
            "https://example.test",
            {"car_selector_car": "33251", "car_selector_make": "5"},
        )
        mock_context.add_cookies.assert_called_once()
        cookies_arg = mock_context.add_cookies.call_args[0][0]
        names = {c["name"] for c in cookies_arg}
        self.assertEqual(names, {"car_selector_car", "car_selector_make"})

    @patch("core.connectors.dtsshop.sync_playwright")
    def test_excecao_do_playwright_vira_supplier_error(self, mock_sync_playwright):
        mock_sync_playwright.side_effect = RuntimeError("chromium nao encontrado")
        with self.assertRaises(SupplierError):
            dtsshop._extract_products_via_browser("https://example.test", None)

    @patch("core.connectors.dtsshop.sync_playwright")
    def test_formato_inesperado_vira_supplier_error(self, mock_sync_playwright):
        # site mudou e devolveu algo que nao e uma lista
        mock_cm, _ = self._mock_playwright({"nao": "e uma lista"})
        mock_sync_playwright.return_value = mock_cm
        with self.assertRaises(SupplierError):
            dtsshop._extract_products_via_browser("https://example.test", None)


class FlattenProductGroupsTests(TestCase):
    def test_monta_url_de_imagem_com_prefixo_de_tamanho(self):
        # Regressao: bug de imagem quebrada (faltava o prefixo "248/", nao
        # vem no JSON do Knockout, e hardcoded no template do site).
        groups = [
            {
                "group_name": "Coilover Suspension",
                "products": [
                    {
                        "id": 143649,
                        "marken_name": "DTSLine",
                        "attribute": {"att_1": {"wert": "299100180"}},
                        "pictorama": [
                            {
                                "url": "https://pictorama-resized.s3.eu-central-1.amazonaws.com/",
                                "id": "kd_33/products/DTSline/299100180/1600_jpg/299100180_001.jpg",
                            }
                        ],
                    }
                ],
            }
        ]
        items = dtsshop._flatten_product_groups(groups)
        self.assertEqual(len(items), 1)
        item = items[0]
        self.assertEqual(item["product_id"], "143649")
        self.assertEqual(item["part_no"], "299100180")
        self.assertEqual(item["brand"], "DTSLine")
        self.assertEqual(
            item["image"],
            "https://pictorama-resized.s3.eu-central-1.amazonaws.com/"
            "248/kd_33/products/DTSline/299100180/1600_jpg/299100180_001.jpg",
        )

    def test_produto_sem_foto_fica_com_image_none(self):
        groups = [{"group_name": "X", "products": [{"id": 1, "attribute": {}}]}]
        items = dtsshop._flatten_product_groups(groups)
        self.assertIsNone(items[0]["image"])


class EnrichWithPriceTests(TestCase):
    """core/search_views.py::_enrich_with_price — junta preço/disponibilidade
    e aplica margem. Depende de PriceTablePoint existir (apply_margin)."""

    def setUp(self):
        # Migration 0005 ja popula a tabela com os pontos reais do cliente —
        # limpa antes pra ter fixture previsivel e isolado nos testes.
        PriceTablePoint.objects.all().delete()
        PriceTablePoint.objects.create(cost=Decimal("10.00"), sale_price=Decimal("29.00"))
        PriceTablePoint.objects.create(cost=Decimal("100.00"), sale_price=Decimal("179.00"))

    @patch("core.search_views.dtsshop.get_price_and_availability")
    def test_aplica_margem_no_preco_do_fornecedor(self, mock_price):
        mock_price.return_value = {
            "1": {"price": "10.00", "availability": {"text": "In stock"}},
        }
        items = [{"product_id": "1", "name": "Peça"}]
        result = _enrich_with_price(items)
        self.assertEqual(result[0]["price"], "29")
        self.assertEqual(result[0]["availability"], {"text": "In stock"})

    @patch("core.search_views.dtsshop.get_price_and_availability")
    def test_fornecedor_devolve_lista_not_found_nao_quebra(self, mock_price):
        # Regressao: bug real em producao — fornecedor devolve
        # ["<id> not found."] (lista) em vez do dict de preco pra alguns
        # produtos (visto em rodas/wheels). _enrich_with_price assumia
        # sempre dict e derrubava a busca inteira com TypeError.
        mock_price.return_value = {"1": ["1 not found."]}
        items = [{"product_id": "1", "name": "Roda sem preço"}]
        result = _enrich_with_price(items)
        self.assertEqual(result[0]["price"], None)
        self.assertEqual(result[0]["availability"], None)

    @patch("core.search_views.dtsshop.get_price_and_availability")
    def test_produto_nao_retornado_pelo_fornecedor_fica_indisponivel(self, mock_price):
        mock_price.return_value = {}
        items = [{"product_id": "999", "name": "Sumiu"}]
        result = _enrich_with_price(items)
        self.assertIsNone(result[0]["price"])

    @patch("core.search_views.dtsshop.get_price_and_availability")
    def test_erro_do_fornecedor_nao_quebra_a_busca(self, mock_price):
        mock_price.side_effect = SupplierError("timeout")
        items = [{"product_id": "1", "name": "Peça"}]
        result = _enrich_with_price(items)
        self.assertIsNone(result[0]["price"])

    def test_lista_vazia_devolve_lista_vazia(self):
        self.assertEqual(_enrich_with_price([]), [])


class ApplyMarginTests(TestCase):
    """core/models.py::apply_margin — ver docs/PRICING.md pra decisão. Cobertura
    completa dos pontos da tabela já foi feita manualmente (task 04 addendum);
    aqui só o suficiente pra travar regressão."""

    def setUp(self):
        PriceTablePoint.objects.all().delete()
        PriceTablePoint.objects.create(cost=Decimal("10.00"), sale_price=Decimal("29.00"))
        PriceTablePoint.objects.create(cost=Decimal("100.00"), sale_price=Decimal("179.00"))
        PriceTablePoint.objects.create(cost=Decimal("3000.00"), sale_price=Decimal("3999.00"))

    def test_ponto_exato_da_tabela(self):
        self.assertEqual(apply_margin(Decimal("100.00")), Decimal("179"))

    def test_interpolacao_entre_pontos(self):
        # meio do caminho entre (10, 29) e (100, 179)
        result = apply_margin(Decimal("55.00"))
        self.assertTrue(Decimal("29") < result < Decimal("179"))

    def test_abaixo_do_primeiro_ponto_mantem_proporcao(self):
        # ratio do primeiro ponto: 29/10 = 2.9 -> 5 * 2.9 = 14.5 -> 15 (ROUND_HALF_UP)
        self.assertEqual(apply_margin(Decimal("5.00")), Decimal("15"))

    def test_acima_do_ultimo_ponto_mantem_proporcao(self):
        # ratio do ultimo ponto: 3999/3000 = 1.333
        result = apply_margin(Decimal("4000.00"))
        self.assertEqual(result, Decimal("5332"))

    def test_tabela_vazia_levanta_erro_em_vez_de_vender_errado(self):
        PriceTablePoint.objects.all().delete()
        with self.assertRaises(ValueError):
            apply_margin(Decimal("50.00"))
