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

package-install-force:
	python3 -m pip install --force-reinstall --user dist/*.whl

selfcheck:
	poetry check

check: selfcheck test lint

.PHONY: install lint test test-coverage selfcheck check build
