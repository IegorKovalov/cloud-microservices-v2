# Run commands from the repository root (where docker-compose.yml lives).

.PHONY: up down

up:
	docker compose up

down:
	docker compose down
