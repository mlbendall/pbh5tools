.PHONY: doc
SHELL = /bin/bash -e

all: build install

build:
	python setup.py build --executable="/usr/bin/env python"

bdist:
	python setup.py build --executable="/usr/bin/env python"
	python setup.py bdist --formats=egg

install:
	python setup.py install

develop:
	python setup.py develop

test:
	find tests -name "*.py" | xargs nosetests
	find tests/cram -name "*.t" | xargs cram 
doc:
	sphinx-apidoc -T -f -o doc src/ && cd doc && make html

doc-clean:
	cd doc && rm -rf modules.rst pbtools.* bash5lib.* cmph5tools.* \
	bash5tools.* _templates _static _build searchindex.js objects.inv

clean: doc-clean
	rm -rf build/;\
	find . -name "*.egg-info" | xargs rm -rf;\
	find . -name "*.pyc" | xargs rm -rf;\
	rm -rf dist/
	rm -f nosetests.xml
	make -C src/C clean
