dev:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml --env-file .env.dev up --build

test:
	docker compose -f docker-compose.test.yml --env-file .env.test up --build --abort-on-container-exit

prod:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml --env-file .env.prod up -d --build

migrate:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml exec backend alembic upgrade head