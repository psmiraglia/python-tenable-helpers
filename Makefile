REPO := psmiraglia
VERSION := 0.1.0a

style: flake8 isort-diff

flake8:
	flake8 setup.py tenable_helpers/*.py tenable_helpers/scripts/*.py

isort-diff:
	isort --diff setup.py tenable_helpers/*.py tenable_helpers/scripts/*.py

isort:
	isort setup.py tenable_helpers/*.py tenable_helpers/scripts/*.py

docker-build:
	docker build --tag $(REPO)/tenable-helpers:$(VERSION) .

docker: docker-build
	docker tag $(REPO)/tenable-helpers:$(VERSION) $(REPO)/tenable-helpers:latest
