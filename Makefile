.PHONY: pull build run parar reiniciar

pull:
	docker compose pull

build:
	docker compose build --no-cache

run: pull
	docker compose up -d --remove-orphans --force-recreate

parar:
	docker compose down

reiniciar: parar run
