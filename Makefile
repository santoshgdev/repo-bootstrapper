# make new REPO=my-service DOPPLER_PROJECT=my-project [DOPPLER_CONFIG=dev] [VISIBILITY=private]
DOPPLER_CONFIG ?= dev
PYTHON_VERSION ?= 3.14
VISIBILITY ?= private
ifeq ($(OS),Windows_NT)
PYTHON ?= python
else
PYTHON ?= python3
endif

.PHONY: new

new:
	$(if $(REPO),,$(error set REPO=name or REPO=owner/name))
	$(if $(DOPPLER_PROJECT),,$(error set DOPPLER_PROJECT))
	$(PYTHON) new_repo.py $(REPO) --doppler-project $(DOPPLER_PROJECT) --doppler-config $(DOPPLER_CONFIG) --python $(PYTHON_VERSION) --visibility $(VISIBILITY)
