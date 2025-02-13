package := 'gandi_pyramid_prometheus'
default_test_suite := 'tests'

install:
    uv sync --group dev

upgrade: && update
    uv lock --upgrade

update:
    #!/bin/bash
    uv sync --group dev
    uv export --no-hashes > .gitlab/ci/requirements.txt

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
    cat CHANGES.rst >> CHANGES.rst.new
    rm CHANGES.rst
    mv CHANGES.rst.new CHANGES.rst
    $EDITOR CHANGES.rst

publish:
    git commit -am "Release $(uv run bin/get_version.py)"
    git tag "v$(uv run bin/get_version.py)"
    git push origin "v$(uv run bin/get_version.py)"
    git push origin main
