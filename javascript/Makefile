# -------------------------------------
# MAKEFILE
# -------------------------------------


#
# commands for artifact cleanup
#

.PHONY: clean
clean: clean.build clean.js

.PHONY: clean.build
clean.build:
	rm -rf dist/

.PHONY: clean.js
clean.js:


#
# commands for testing
#

.PHONY: test
test: test.unittests test.lint

.PHONY: test.lint
test.lint:
	# ?

.PHONY: test.unittests
test.unittests:
	# PYTHONPATH=${PYTHONPATH} python runtests.py

.PHONY: test.sdk.node
test.sdk.node:
	node ../test_scripts/test.node.js

.PHONY: test.sdk.browser
test.sdk.browser:
	node ../test_scripts/test.browser.js


#
# commands for packaging and deploying to npmjs.com
#

.PHONY: build
build: test
	npm i --prefix .
	npm run --prefix . bundle

.PHONY: release
release: clean build
	npm publish
