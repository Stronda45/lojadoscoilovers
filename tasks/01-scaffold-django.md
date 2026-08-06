# 01 — Scaffold Django + DRF

Estimativa: 3h · Bloqueada por: nada · **Status: concluída (com 1 desvio)**

## Objetivo
Base do projeto para as demais tarefas rodarem em cima.

## Tarefas
- [x] `django-admin startproject` + app principal (`core`)
- [x] Django REST Framework instalado e configurado
- [x] ~~PostgreSQL configurado (local via docker-compose ou instalação direta)~~ —
      **SQLite local por enquanto** (Postgres via Homebrew está com lib `icu4c`
      quebrada; sem Docker instalado; consertar custaria tempo do sprint de 2
      semanas). Produção continua Postgres via Railway (task 10). Detalhes no
      `README.md`.
- [x] CORS liberado para o frontend local (`django-cors-headers`, origem
      `http://localhost:3000` via `.env`)
- [x] `.env` para variáveis (secret key, debug, allowed hosts, CORS) — no
      `.gitignore`, não commitado
- [x] `GET /health` respondendo 200 — testado com curl, `{"status":"ok"}`
- [x] README com instruções de setup local

## Aceite
- [x] `python manage.py runserver` sobe sem erro
- [x] `GET /health` funciona
- [ ] Alguém consegue clonar e rodar local seguindo só o README — não testado por
      terceiro ainda, só localmente

## Versões (fixadas em `requirements.txt`)
Django==5.2.17 (não 6.1 — incompatível com DRF atual), djangorestframework==3.17.2,
django-cors-headers==4.9.0, python-dotenv==1.2.2
