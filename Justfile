package := 'gandi_pyramid_prometheus'
default_test_suite := 'tests'

install:
    uv sync --group dev


test: lint unittest

lint:
    uv run ruff check .

unittest test_suite=default_test_suite:
    uv run pytest -sxv {{test_suite}}

fmt:
    uv run ruff check --fix .
    uv run ruff format src tests

cov test_suite=default_test_suite:
    rm -f .coverage
    rm -rf htmlcov
    uv run pytest --cov-report=html --cov={{package}} {{test_suite}}
    xdg-open htmlcov/index.html

release major_minor_patch: test && changelog
    uvx --with=pdm,pdm-bump --python-preference system pdm bump {{major_minor_patch}}

changelog:
    uv run python bin/write_changelog.py
    cat CHANGELOG.rst >> CHANGELOG.rst.new
    rm CHANGELOG.rst
    mv CHANGELOG.rst.new CHANGELOG.rst
    $EDITOR CHANGELOG.rst

publish:
    git commit -am "Release $(uv run scripts/get_version.py)"
    git tag "v$(uv run scripts/get_version.py)"
    git push origin "v$(uv run scripts/get_version.py)"
    git push origin main
