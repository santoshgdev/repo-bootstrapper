IMAGE ?= ${name}:dev

.PHONY: build lock

build:
	docker build -t $$(IMAGE) .

# Writes uv.lock back into the repo; rebuild afterwards.
lock:
	docker run --rm -v "$$(CURDIR):/app" --entrypoint uv $$(IMAGE) lock
