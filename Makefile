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

gendiff:
	poetry run gendiff

diff:
	poetry run gendiff gendiff/files/file1.json gendiff/files/file2.json

package-install-force: 
	python3 -m pip install --force-reinstall --user dist/*.whl

selfcheck:
	poetry check

check: selfcheck lint

.PHONY: install lint selfcheck check build