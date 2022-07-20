style: flake8 isort-diff

flake8:
	flake8 *.py

isort-diff:
	isort --diff *.py

isort:
	isort *.py
