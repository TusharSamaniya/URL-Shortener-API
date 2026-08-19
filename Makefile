# ─── Configuration ────────────────────────────────────────────────────────────
DOCKER_USER   ?= your-dockerhub-username
IMAGE_API     := $(DOCKER_USER)/url-shortener-api
IMAGE_FRONTEND := $(DOCKER_USER)/url-shortener-frontend
TAG           ?= latest

# ─── Local Development ────────────────────────────────────────────────────────
.PHONY: up
up:
	docker compose up --build

.PHONY: down
down:
	docker compose down -v

.PHONY: test
test:
	cd backend && pip install -r requirements.txt -q && pytest test_api.py -v

# ─── Docker Hub ───────────────────────────────────────────────────────────────
.PHONY: build
build:
	docker build -t $(IMAGE_API):$(TAG) ./backend
	docker build -t $(IMAGE_FRONTEND):$(TAG) ./frontend

.PHONY: push
push: build
	docker push $(IMAGE_API):$(TAG)
	docker push $(IMAGE_FRONTEND):$(TAG)

.PHONY: pull-run
## Pull from Docker Hub and run (no build needed)
pull-run:
	docker pull $(IMAGE_API):$(TAG)
	docker pull $(IMAGE_FRONTEND):$(TAG)
	docker compose up
