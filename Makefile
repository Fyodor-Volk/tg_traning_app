SHELL := /bin/sh

COMPOSE := docker compose
DEV_FILE := -f docker-compose.dev.yml

.PHONY: help up up-dev down down-dev build build-dev logs logs-dev ps ps-dev restart restart-dev clean db-only

help:
	@printf "%s\n" \
	"Targets:" \
	"  up           Start prod stack (docker-compose.yml)" \
	"  up-dev       Start dev stack (docker-compose.dev.yml)" \
	"  down         Stop prod stack" \
	"  down-dev     Stop dev stack" \
	"  build        Build prod images" \
	"  build-dev    Build dev images" \
	"  logs         Tail prod logs" \
	"  logs-dev     Tail dev logs" \
	"  ps           Show prod containers" \
	"  ps-dev       Show dev containers" \
	"  restart      Restart prod stack" \
	"  restart-dev  Restart dev stack" \
	"  clean        Stop and remove prod containers, networks" \
	"  db-only      Start only database (prod compose)"

up:
	$(COMPOSE) up --build

up-dev:
	$(COMPOSE) $(DEV_FILE) up

down:
	$(COMPOSE) down

down-dev:
	$(COMPOSE) $(DEV_FILE) down

build:
	$(COMPOSE) build

build-dev:
	$(COMPOSE) $(DEV_FILE) build

logs:
	$(COMPOSE) logs -f --tail=200

logs-dev:
	$(COMPOSE) $(DEV_FILE) logs -f --tail=200

ps:
	$(COMPOSE) ps

ps-dev:
	$(COMPOSE) $(DEV_FILE) ps

restart: down up

restart-dev: down-dev up-dev

clean: down
	$(COMPOSE) rm -f

db-only:
	$(COMPOSE) up db
