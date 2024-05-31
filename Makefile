.PHONY dev:
dev:
	poetry run uvicorn src.main:app --reload

.PHONY format:
format:	
	poetry run black src
	poetry run ruff check src