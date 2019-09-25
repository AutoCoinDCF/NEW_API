init:
	pip install -r requirements.txt

test:
	pytest --doctest-modules --doctest-continue-on-failure --cov api/ --cov-report term-missing --cov-config .coveragerc api/ tests/
	flake8 ./api --exclude __init__.py
