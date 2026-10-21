.PHONY: install test lint run demo
install:
	pip install -e '.[dev,demo]'
test:
	pytest -q
lint:
	ruff check src tests demo benchmarks
run:
	uvicorn rinvo.api:app --reload --host 127.0.0.1 --port 8000
demo:
	python demo/app.py
