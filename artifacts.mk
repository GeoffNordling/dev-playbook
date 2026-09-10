# The cloa-viewer page. Its end-to-end tests drive the built page, and both
# dist/ and node_modules/ are gitignored, so no fresh checkout or worktree
# carries either: the gate builds them rather than asking to be reminded.
WEB := src/dev_playbook/cloa_viewer/web
WEB_SRC := $(WEB)/index.html $(WEB)/vite.config.ts $(WEB)/tsconfig.json \
	$(shell find $(WEB)/src -type f)
ARTIFACTS := $(WEB)/dist/index.html

# touch: npm leaves the directory mtime behind the lockfile on a no-op
# install, which would re-run ci on every make.
$(WEB)/node_modules: $(WEB)/package-lock.json
	npm --prefix $(WEB) ci
	touch $@

$(WEB)/dist/index.html: $(WEB)/node_modules $(WEB_SRC)
	npm --prefix $(WEB) run build
