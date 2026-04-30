# Run commands from the repository root (where docker-compose.yml lives).

.PHONY: up down test logs demo

up:
	docker compose up --build

down:
	docker compose down

test:
	python3 -m pytest tests -v

logs:
	docker compose logs -f

demo:
	curl -s -X POST http://localhost:8000/process \
		-H 'Content-Type: application/json' \
		-d '{"pixels":[0.1,0.9,0.5],"threshold":0.5}'
