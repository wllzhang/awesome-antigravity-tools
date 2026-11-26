.PHONY: all validate generate export build-site test mcp-test audit discover doctor serve

all: generate validate test mcp-test

generate:
	python3 scripts/aat_cli.py sync

validate:
	python3 scripts/aat_cli.py verify --check-sync --strict-warnings

export:
	python3 scripts/export_catalog.py

build-site:
	python3 scripts/build_site.py

test:
	python3 -m unittest discover -s tests -v
	node --check docs/catalog-logic.js
	node --check docs/insights.js
	node --check docs/app.js
	node --test tests/test_web.mjs

mcp-test:
	python3 scripts/mcp_server.py --self-test

audit:
	python3 scripts/health-check.py --use-gh-cli
	$(MAKE) generate

discover:
	python3 scripts/discover_candidates.py --use-gh-cli --limit 15

doctor:
	python3 scripts/aat_cli.py doctor

serve:
	python3 -m http.server 8765 --directory docs
