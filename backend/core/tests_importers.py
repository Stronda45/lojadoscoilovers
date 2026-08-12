"""Testes do catálogo importado (Fase 2, task 04) — parsers, segurança do
upload e idempotência do serviço de import. Amostras inline pequenas (não os
arquivos reais, que são grandes demais pra versionar) mas no formato exato
confirmado nos arquivos reais do cliente (2026-08-12)."""

import io
import zipfile
from decimal import Decimal

from django.contrib.auth.models import Group, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings

from core.importers.base import parse_decimal_european, sanitize_text
from core.importers.mts import parse_mts
from core.importers.security import (
    MAX_UPLOAD_SIZE,
    UploadValidationError,
    safe_read_zip_member,
    validate_upload,
)
from core.importers.service import import_supplier_file
from core.importers.ta_technix import _parse_makes, parse_ta_technix_csv, parse_ta_technix_zip
from core.models import ImportedProduct, ImportedProductFitment, Supplier

MTS_HEADER = (
    "category_name;part_number;name;make;model;series;housing;engine;type;hsn;tsn;year;"
    "body_type;drive_type;fuel_type;capacity_ccm;power_kw;power_km;number_of_cylinders;code;"
    "engine_code;max_axle_load_fa;max_axle_load_ra;lowering_fa;lowering_ra;"
    "with_camber_plates_fa;with_camber_plates_ra;additional_information;tuv_certificate;"
    "eg_type_approval_number_from;eg_type_approval_number_to;approval_number;"
    "additional_adjustment_fa;additional_adjustment_ra;axle;additional_lowering;"
    "adjustment_camber_range;adjustment_caster_range;fitting_for_oem_suspension;weight;"
    "version;replaces;compatibility;in_sets;a_piston_rod_diameter;b_piston_rod_thread_pitch;"
    "c_length_of_the_groove;d_piston_rod_thread_length;dedicated_spring_inside_diameter;"
    "msrp;product_notes;images"
)


def _mts_row(**overrides):
    fields = {
        "category_name": "Coilover kits", "part_number": "MTSTEST01", "name": "Coilover Test",
        "make": "BMW", "model": "3 Series", "series": "", "housing": "", "engine": "320d",
        "type": "", "hsn": "", "tsn": "", "year": "01/15 -", "body_type": "Sedan",
        "drive_type": "RWD", "fuel_type": "Diesel", "capacity_ccm": "", "power_kw": "",
        "power_km": "", "number_of_cylinders": "", "code": "", "engine_code": "",
        "max_axle_load_fa": "", "max_axle_load_ra": "", "lowering_fa": "", "lowering_ra": "",
        "with_camber_plates_fa": "", "with_camber_plates_ra": "", "additional_information": "",
        "tuv_certificate": "", "eg_type_approval_number_from": "", "eg_type_approval_number_to": "",
        "approval_number": "", "additional_adjustment_fa": "", "additional_adjustment_ra": "",
        "axle": "", "additional_lowering": "", "adjustment_camber_range": "",
        "adjustment_caster_range": "", "fitting_for_oem_suspension": "", "weight": "",
        "version": "", "replaces": "", "compatibility": "", "in_sets": "",
        "a_piston_rod_diameter": "", "b_piston_rod_thread_pitch": "", "c_length_of_the_groove": "",
        "d_piston_rod_thread_length": "", "dedicated_spring_inside_diameter": "",
        "msrp": "707,25", "product_notes": "Nota do produto",
        "images": "https://example.test/a.jpg,https://example.test/b.jpg",
    }
    fields.update(overrides)
    order = MTS_HEADER.split(";")
    return ";".join(fields[k] for k in order)


class SanitizeTextTests(TestCase):
    def test_neutraliza_formula_csv_injection(self):
        self.assertEqual(sanitize_text("=cmd|'/c calc'!A1"), "'=cmd|'/c calc'!A1")
        self.assertEqual(sanitize_text("+1+1"), "'+1+1")
        self.assertEqual(sanitize_text("texto normal"), "texto normal")

    def test_valor_vazio(self):
        self.assertEqual(sanitize_text(None), "")
        self.assertEqual(sanitize_text(""), "")


class ParseDecimalEuropeanTests(TestCase):
    def test_formatos_reais_confirmados_nos_arquivos(self):
        # "699" (MTS, sem casas decimais) e "707,25" / "1.399,00" (MTS e TA
        # Technix, com casas decimais) — mesmo formato europeu nos 2.
        self.assertEqual(parse_decimal_european("699"), Decimal("699"))
        self.assertEqual(parse_decimal_european("707,25"), Decimal("707.25"))
        self.assertEqual(parse_decimal_european("1.399,00"), Decimal("1399.00"))

    def test_valor_vazio_ou_invalido(self):
        self.assertIsNone(parse_decimal_european(""))
        self.assertIsNone(parse_decimal_european(None))
        self.assertIsNone(parse_decimal_european("não é número"))


class ParseMtsTests(TestCase):
    def test_extrai_produto_e_fitment(self):
        content = MTS_HEADER + "\n" + _mts_row()
        products = parse_mts(content.encode("utf-8-sig"))
        self.assertEqual(len(products), 1)
        p = products["MTSTEST01"]
        self.assertEqual(p.title, "Coilover Test")
        # regressao: formato europeu, nao ponto — bug real encontrado testando
        # contra o arquivo de verdade da MTS.
        self.assertEqual(p.cost_price, Decimal("707.25"))
        self.assertEqual(p.category, "Coilover kits")
        self.assertEqual(p.image_url, "https://example.test/a.jpg")
        self.assertEqual(len(p.fitments), 1)
        self.assertEqual(p.fitments[0]["make"], "BMW")

    def test_mesmo_part_number_em_varias_linhas_vira_1_produto_com_2_fitments(self):
        content = MTS_HEADER + "\n" + _mts_row(model="3 Series") + "\n" + _mts_row(model="4 Series")
        products = parse_mts(content.encode("utf-8-sig"))
        self.assertEqual(len(products), 1)
        self.assertEqual(len(products["MTSTEST01"].fitments), 2)

    def test_linha_sem_part_number_e_ignorada(self):
        content = MTS_HEADER + "\n" + _mts_row(part_number="")
        products = parse_mts(content.encode("utf-8-sig"))
        self.assertEqual(products, {})


class ParseMakesTests(TestCase):
    """TA Technix: 'Hersteller' pode ter varias marcas juntas ou ser lixo
    (peca universal) — achado real inspecionando os dados."""

    def test_multiplas_marcas_com_prefixo_alemao(self):
        self.assertEqual(_parse_makes("passend für  Audi / Seat / VW"), ["Audi", "Seat", "VW"])

    def test_marca_unica(self):
        self.assertEqual(_parse_makes("passend für Smart"), ["Smart"])

    def test_valores_de_peca_universal_viram_lista_vazia(self):
        self.assertEqual(_parse_makes("Universell"), [])
        self.assertEqual(_parse_makes("1 Set"), [])
        self.assertEqual(_parse_makes(""), [])


class ParseTaTechnixTests(TestCase):
    def _row(self, hersteller="passend für Smart", netto_ek="849,00", uvp="1.399,00"):
        fields = ["ta1", "EAN1", hersteller, "Fortwo", "453", "2015 -",
                  "Titulo DE#Z#Zresto", "Titulo EN#Z#Zresto", uvp, netto_ek] + [""] * 21 + [
                      "1 Set", "", "https://example.test/img.jpg", ""]
        return ";".join(f'"{v}"' for v in fields)

    def test_usa_netto_ek_como_custo_nao_uvp(self):
        content = self._row()
        products = parse_ta_technix_csv(content.encode("utf-8-sig"))
        p = products["ta1"]
        self.assertEqual(p.cost_price, Decimal("849.00"))
        self.assertEqual(p.raw_attributes["uvp_sugerido"], "1.399,00")

    def test_quebra_de_linha_zeta_vira_newline_na_descricao(self):
        content = self._row()
        products = parse_ta_technix_csv(content.encode("utf-8-sig"))
        p = products["ta1"]
        self.assertIn("\n", p.description)
        self.assertNotIn("#Z", p.description)

    def test_le_csv_de_dentro_de_um_zip(self):
        csv_content = (self._row() + "\n").encode("utf-8-sig")
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("CSV Kopfzeile 01.csv", "cabecalho, nao usado")
            zf.writestr("TA Technix Preisliste CSV_Export 99999 1 20260101.csv", csv_content)
        products = parse_ta_technix_zip(buf.getvalue())
        self.assertEqual(len(products), 1)


class UploadSecurityTests(TestCase):
    def test_extensao_nao_permitida_rejeitada(self):
        with self.assertRaises(UploadValidationError):
            validate_upload("malware.exe", 100, b"MZ\x90\x00")

    def test_tamanho_acima_do_limite_rejeitado(self):
        with self.assertRaises(UploadValidationError):
            validate_upload("grande.csv", MAX_UPLOAD_SIZE + 1, b"a,b,c")

    def test_extensao_csv_com_conteudo_binario_rejeitada(self):
        with self.assertRaises(UploadValidationError):
            validate_upload("fake.csv", 100, b"\x00\x01\x02binario")

    def test_extensao_xlsx_sem_assinatura_zip_rejeitada(self):
        # .xlsx e internamente um zip (assinatura "PK") — um arquivo
        # renomeado pra .xlsx sem ser zip de verdade tem que ser rejeitado.
        with self.assertRaises(UploadValidationError):
            validate_upload("fake.xlsx", 100, b"nao e um zip")

    def test_csv_valido_passa(self):
        ext = validate_upload("dados.csv", 100, b"col1;col2\nval1;val2")
        self.assertEqual(ext, ".csv")

    def test_zip_bomb_protecao(self):
        # zip minusculo que alega descomprimir pra alem do limite
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("Preisliste.csv", "a" * 1000)
        zip_bytes = buf.getvalue()
        # forca o teste de tamanho descomprimido mockando o limite baixo
        import core.importers.security as security_module
        original_limit = security_module.MAX_UNCOMPRESSED_ZIP_SIZE
        security_module.MAX_UNCOMPRESSED_ZIP_SIZE = 10
        try:
            with self.assertRaises(UploadValidationError):
                safe_read_zip_member(zip_bytes, "Preisliste")
        finally:
            security_module.MAX_UNCOMPRESSED_ZIP_SIZE = original_limit


class ImportSupplierFileServiceTests(TestCase):
    def test_idempotente_nao_duplica_ao_rodar_2x(self):
        content = (MTS_HEADER + "\n" + _mts_row()).encode("utf-8-sig")

        r1 = import_supplier_file("mts", "arquivo.csv", content)
        self.assertEqual(r1.created, 1)
        self.assertEqual(ImportedProduct.objects.count(), 1)

        r2 = import_supplier_file("mts", "arquivo.csv", content)
        self.assertEqual(r2.created, 0)
        self.assertEqual(r2.updated, 1)
        self.assertEqual(ImportedProduct.objects.count(), 1)
        self.assertEqual(ImportedProductFitment.objects.count(), 1)

    def test_deactivate_escopado_por_categoria_nao_apaga_outra_categoria(self):
        # regressao: bug real encontrado testando contra os arquivos reais —
        # a MTS manda 1 arquivo por categoria; importar a categoria B nao
        # pode desativar o que ja foi importado da categoria A.
        springs = (MTS_HEADER + "\n" + _mts_row(
            category_name="Adjustable Springs", part_number="SPRING1",
        )).encode("utf-8-sig")
        import_supplier_file("mts", "springs.csv", springs)

        camber = (MTS_HEADER + "\n" + _mts_row(
            category_name="Camber plates", part_number="CAMBER1",
        )).encode("utf-8-sig")
        result = import_supplier_file("mts", "camber.csv", camber)

        self.assertEqual(result.deactivated, 0)
        self.assertTrue(ImportedProduct.objects.get(external_reference="SPRING1").active)
        self.assertTrue(ImportedProduct.objects.get(external_reference="CAMBER1").active)

    def test_produto_sumido_do_arquivo_fica_inactive_nao_apagado(self):
        row1 = _mts_row(part_number="A1", category_name="Coilover kits")
        row2 = _mts_row(part_number="A2", category_name="Coilover kits")
        content_v1 = (MTS_HEADER + "\n" + row1 + "\n" + row2).encode("utf-8-sig")
        import_supplier_file("mts", "v1.csv", content_v1)

        content_v2 = (MTS_HEADER + "\n" + row1).encode("utf-8-sig")  # A2 sumiu
        result = import_supplier_file("mts", "v2.csv", content_v2)

        self.assertEqual(result.deactivated, 1)
        a2 = ImportedProduct.objects.get(external_reference="A2")
        self.assertFalse(a2.active)  # nao foi apagado, so desativado

    def test_fornecedor_desconhecido_rejeitado(self):
        with self.assertRaises(UploadValidationError):
            import_supplier_file("fornecedor-inventado", "x.csv", b"a,b")

    def test_extensao_errada_pro_fornecedor_rejeitada(self):
        # MTS espera .csv, nao .xlsx
        with self.assertRaises(UploadValidationError):
            import_supplier_file("mts", "arquivo.xlsx", b"PK\x03\x04resto")


class SupplierModelTests(TestCase):
    def test_slug_unico(self):
        Supplier.objects.create(name="MTS", slug="mts")
        with self.assertRaises(Exception):
            Supplier.objects.create(name="MTS 2", slug="mts")


class ImportedProductSalePriceTests(TestCase):
    def setUp(self):
        from core.models import PriceTablePoint
        PriceTablePoint.objects.all().delete()
        PriceTablePoint.objects.create(cost=Decimal("10.00"), sale_price=Decimal("29.00"))
        PriceTablePoint.objects.create(cost=Decimal("100.00"), sale_price=Decimal("179.00"))

    def test_sale_price_aplica_margem_sobre_custo(self):
        supplier = Supplier.objects.create(name="MTS", slug="mts")
        product = ImportedProduct.objects.create(
            supplier=supplier, external_reference="X1", title="Teste",
            cost_price=Decimal("100.00"),
        )
        self.assertEqual(product.sale_price, Decimal("179"))

    def test_sem_custo_sale_price_e_none(self):
        supplier = Supplier.objects.create(name="Cheney", slug="cheney")
        product = ImportedProduct.objects.create(
            supplier=supplier, external_reference="R1", title="Roda sem preço",
            cost_price=None,
        )
        self.assertIsNone(product.sale_price)


@override_settings(ALLOWED_HOSTS=["testserver"])
class AdminUploadViewTests(TestCase):
    """Endpoint de upload vive dentro do Django Admin (sessão), não como API
    de token — decisão da task 02 (painel = Django Admin). Cobre a
    permissão: `admin_view()` sozinho só garante is_staff, não permissão de
    model pra URLs custom — achado real testando (funcionário conseguia
    acessar a página de upload só adivinhando a URL, sem ter permissão em
    ImportedProduct)."""

    def setUp(self):
        User.objects.filter(username__in=["dono", "funcionario", "anonimo"]).delete()
        self.dono = User.objects.create_superuser(
            username="dono", password="x", email="dono@example.com"
        )
        self.funcionario = User.objects.create_user(
            username="funcionario", password="x", is_staff=True,
        )
        group, _ = Group.objects.get_or_create(name="Funcionário")
        self.funcionario.groups.add(group)

    def test_dono_acessa_pagina_de_upload(self):
        client = Client()
        client.login(username="dono", password="x")
        resp = client.get("/admin/core/importedproduct/upload/")
        self.assertEqual(resp.status_code, 200)

    def test_funcionario_sem_permissao_e_bloqueado(self):
        client = Client()
        client.login(username="funcionario", password="x")
        resp = client.get("/admin/core/importedproduct/upload/")
        self.assertEqual(resp.status_code, 403)

    def test_sem_login_redireciona(self):
        client = Client()
        resp = client.get("/admin/core/importedproduct/upload/")
        self.assertEqual(resp.status_code, 302)

    def test_upload_de_verdade_cria_produtos(self):
        content = (MTS_HEADER + "\n" + _mts_row()).encode("utf-8-sig")
        client = Client()
        client.login(username="dono", password="x")
        upload = SimpleUploadedFile("adjustable-springs.csv", content, content_type="text/csv")
        resp = client.post(
            "/admin/core/importedproduct/upload/",
            {"supplier": "mts", "file": upload},
            follow=True,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(ImportedProduct.objects.count(), 1)
