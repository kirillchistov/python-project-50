install:
	poetry install

build: check
	poetry build

publish:
	poetry publish --dry-run

package-install:
	python3 -m pip install --user dist/*.whl

lint:
	poetry run flake8 gendiff

test:
	poetry run pytest

test-coverage:
	poetry run pytest --cov=gendiff --cov-report=xml

gendiff:
	poetry run gendiff

diff:
	poetry run gendiff gendiff/files/file1.json gendiff/files/file2.json

diff-yaml:
	poetry run gendiff gendiff/files/file1.yml gendiff/files/file2.yml

diff-nested:
	poetry run gendiff gendiff/files/nested1.json gendiff/files/nested2.json

diff-plain:
	poetry run gendiff --format plain gendiff/files/nested1.json gendiff/files/nested2.json

diff-json:
	poetry run gendiff --format json gendiff/files/nested1.json gendiff/files/nested2.json

package-install-force:
	python3 -m pip install --force-reinstall --user dist/*.whl

selfcheck:
	poetry check

check: selfcheck test lint

dsa-lab:
	poetry run uvicorn dsa_lab.app:app --reload --host 127.0.0.1 --port 8000

dsa-lint:
	poetry run flake8 dsa_lab tests/test_dsa_lab.py

dsa-pages:
	poetry run python -m dsa_lab.export_static --out site

dsa-pages-preview: dsa-pages
	python3 -m http.server 8080 --directory site

.PHONY: install lint test test-coverage selfcheck check build dsa-lab dsa-lint dsa-pages dsa-pages-preview
