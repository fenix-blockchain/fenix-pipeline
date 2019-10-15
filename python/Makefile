# -------------------------------------
# MAKEFILE
# -------------------------------------

VIRTUAL_ENV ?= ${PWD}/env
PYTHON=${VIRTUAL_ENV}/bin/python


#
# commands for artifact cleanup
#

.PHONY: clean
clean: clean.build clean.pyc

.PHONY: clean.build
clean.build:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info

.PHONY: clean.pyc
clean.pyc:
	find . -name '*.pyc' -delete
	find . -name '*.pyo' -delete
	rm -rf .pytest_cache


#
# commands for testing
#

.PHONY: test
test: test.unittests test.flake8

.PHONY: test.flake8
test.flake8:
	flake8 .

.PHONY: test.unittests
test.unittests:
	# PYTHONPATH=${PYTHONPATH} python runtests.py

.PHONY: test.sdk
test.sdk:
	PYTHONPATH=${PWD}:${PYTHONPATH} LOG_LEVEL=INFO ${PYTHON} ../test_scripts/test.py

.PHONY: test.sdk.prod
test.sdk.prod:
	PYTHONPATH=${PWD}:${PYTHONPATH} LOCAL_ONLY=false LOG_LEVEL=INFO ${PYTHON} ../test_scripts/test.py


#
# commands for packaging and deploying to pypi
#

.PHONY: build
build: test
	python setup.py sdist
	python setup.py bdist_wheel

.PHONY: release
release: clean build
	twine upload dist/*
