PYTHON := .venv/bin/python3

.PHONY: run migrate makemigrations shell install health

install:
	python3 -m venv .venv
	$(PYTHON) -m pip install --upgrade pip -q
	$(PYTHON) -m pip install -r requirements.txt -q
	$(PYTHON) -m playwright install chromium

run:
	$(PYTHON) manage.py runserver

migrate:
	$(PYTHON) manage.py migrate

makemigrations:
	$(PYTHON) manage.py makemigrations

shell:
	$(PYTHON) manage.py shell

health:
	curl -s http://127.0.0.1:8000/health && echo ""
