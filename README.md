# lojadoscoilovers — backend

Django + DRF. Ver `docs/STACK.md` para stack completa e `tasks/` para o plano da Fase 1.

## Setup local

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # se existir; senão usar o .env já commitado localmente (ver nota)
python manage.py migrate
python manage.py runserver
```

`GET http://127.0.0.1:8000/health` deve responder `{"status": "ok"}`.

## Banco de dados

**Local: SQLite** (padrão do Django, zero setup). O Postgres local via Homebrew
(`postgresql@13`) está com uma dependência quebrada (`icu4c`) — não foi consertado
por falta de tempo (sprint de 2 semanas). Não bloqueia o desenvolvimento porque o
Django ORM abstrai a maior parte das diferenças.

**Produção: PostgreSQL** (Railway). Antes do deploy (task 10), revisar se algum
código depende de comportamento específico do SQLite.

## Variáveis de ambiente (`.env`, não commitado)

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `DJANGO_ALLOWED_HOSTS`
- `CORS_ALLOWED_ORIGINS`
