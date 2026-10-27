# repo-bootstrapper

Template repo for Python projects that run in Docker with uv, with secrets injected by `doppler run`.

## One command

```bash
make new REPO=my-service DOPPLER_PROJECT=my-project   # optional: DOPPLER_CONFIG=dev VISIBILITY=private PYTHON_VERSION=3.14
```

Creates the GitHub repo from this template, runs **Initialize repo**, waits for it, clones it next to this repo,
removes the init workflow, then runs `make build` and `make pycharm`. Needs `gh` (logged in with the `workflow` scope), git and Docker.

## New repo on GitHub, by hand

1. Create a repo from this template ("Use this template", or `gh repo create NAME --template santoshgdev/repo-bootstrapper`).
2. In the new repo, run **Actions → Initialize repo** with the Doppler project and config.
   It renders `templates/` into the repo root, deletes the bootstrapper files, and commits.
3. Delete `.github/workflows/init.yml` yourself; the workflow's token isn't allowed to change workflow files.

## Local

```bash
python bootstrap.py example.toml --dest ../my-project
```

Flags (`--name`, `--python`, `--doppler-project`, `--doppler-config`) override the config file.

## What a generated repo needs at run time

`DOPPLER_TOKEN`: a read-only service token for the chosen project/config. Never commit it.

## PyCharm

1. `make build`, then add a Docker interpreter on image `<name>:dev` and name it `<name> docker`.
2. `make pycharm` installs the `handler` run config into `.idea/runConfigurations/` (gitignored).
3. Fill in `DOPPLER_TOKEN` in that run config. The image's `doppler run` entrypoint injects the secrets.
