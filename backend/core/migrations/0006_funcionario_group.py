# Cria o grupo "Funcionário" (Fase 2, task 02 — painel admin). Ve/atualiza
# pedidos e ve dados do cliente (precisa pra cumprir o pedido no fornecedor),
# mas nao mexe em precificacao (PriceTablePoint) nem em outras contas
# (auth.User/Group).
#
# `create_permissions` chamado explicitamente porque as permissoes de
# view/change/etc sao criadas pelo sinal post_migrate, que so dispara DEPOIS
# de todas as migrations rodarem — numa instalacao nova (0001..0006 na mesma
# chamada de `migrate`), elas ainda nao existem no momento em que esta
# migration roda.

from django.apps import apps as global_apps
from django.contrib.auth.management import create_permissions
from django.db import migrations

PERMISSIONS = [
    "view_customer",
    "view_order",
    "change_order",
    "view_orderitem",
]


def create_group(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    create_permissions(global_apps.get_app_config("core"), verbosity=0, using=db_alias)

    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    group, _ = Group.objects.using(db_alias).get_or_create(name="Funcionário")
    perms = Permission.objects.using(db_alias).filter(
        content_type__app_label="core",
        codename__in=PERMISSIONS,
    )
    group.permissions.set(perms)


def remove_group(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.using(schema_editor.connection.alias).filter(name="Funcionário").delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_seed_price_table_points'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(create_group, remove_group),
    ]
