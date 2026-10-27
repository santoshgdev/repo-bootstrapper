IMAGE ?= ${name}:dev
RUN_CONFIG := .idea/runConfigurations/handler.xml
# Recipes must work under cmd.exe (Windows make) as well as sh.
ifeq ($$(OS),Windows_NT)
PYTHON ?= python
else
PYTHON ?= python3
endif

.PHONY: build lock pycharm

build:
	docker build -t $$(IMAGE) .

# Writes uv.lock back into the repo; rebuild afterwards.
lock:
	docker run --rm -v "$$(CURDIR):/app" --entrypoint uv $$(IMAGE) lock

# Installs the PyCharm run config; never overwrites one you've already filled in.
pycharm:
	$$(PYTHON) -c "import pathlib, shutil; p = pathlib.Path('$$(RUN_CONFIG)'); p.parent.mkdir(parents=True, exist_ok=True); p.exists() or shutil.copy('pycharm/handler.run.xml', p)"
	@echo Fill DOPPLER_TOKEN in the handler run config at $$(RUN_CONFIG) - it is gitignored.
