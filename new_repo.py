"""Create a GitHub repo from this template, initialize it, clone it, and set it up locally.

Usage: python new_repo.py REPO --doppler-project P [--doppler-config dev] [--python 3.14]
                          [--visibility private|public] [--dest DIR] [--no-build]
REPO is a name or OWNER/NAME; the project name is REPO lowercased with _ -> -.
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

import bootstrap

HERE = Path(__file__).parent
TEMPLATE = "santoshgdev/repo-bootstrapper"
WORKFLOW = "init.yml"


def run(*cmd: str, cwd: Path | None = None, capture: bool = False) -> str:
    print("+", " ".join(cmd), flush=True)
    result = subprocess.run(cmd, cwd=cwd, check=True, text=True,
                            stdout=subprocess.PIPE if capture else None)
    return result.stdout.strip() if capture else ""


def wait_for(what: str, check, timeout: int = 90, every: int = 3):
    """Poll check() until it returns something truthy; give up after timeout seconds."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        found = check()
        if found:
            return found
        time.sleep(every)
    raise SystemExit(f"timed out after {timeout}s waiting for {what}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("repo")
    ap.add_argument("--doppler-project", required=True)
    ap.add_argument("--doppler-config", default="dev")
    ap.add_argument("--python", default="3.14")
    ap.add_argument("--visibility", choices=("private", "public"), default="private")
    ap.add_argument("--dest", type=Path, help="defaults to a sibling of this repo")
    ap.add_argument("--no-build", action="store_true", help="skip make build / make pycharm")
    args = ap.parse_args()

    owner, _, name = args.repo.rpartition("/")
    owner = owner or run("gh", "api", "user", "--jq", ".login", capture=True)
    full = f"{owner}/{name}"
    project = name.lower().replace("_", "-")
    # Validate before touching GitHub.
    values = bootstrap.load_values(None, {
        "name": project, "python": args.python,
        "doppler_project": args.doppler_project, "doppler_config": args.doppler_config,
    })
    dest = args.dest or HERE.parent / name
    if dest.exists():
        raise SystemExit(f"{dest} already exists")

    run("gh", "repo", "create", full, f"--{args.visibility}", "--template", TEMPLATE)
    wait_for("the init workflow to appear", lambda: WORKFLOW in run(
        "gh", "workflow", "list", "-R", full, "--json", "path", capture=True))

    run("gh", "workflow", "run", WORKFLOW, "-R", full,
        "-f", f"name={project}", "-f", f"python={args.python}",
        "-f", f"doppler_project={args.doppler_project}",
        "-f", f"doppler_config={args.doppler_config}")
    run_id = wait_for("the init run to start", lambda: json.loads(run(
        "gh", "run", "list", "-R", full, "--workflow", WORKFLOW,
        "--json", "databaseId", "--limit", "1", capture=True)))[0]["databaseId"]
    run("gh", "run", "watch", str(run_id), "-R", full, "--exit-status", "--interval", "5")

    run("gh", "repo", "clone", full, str(dest))
    # The workflow's token can't touch workflow files; your gh login can.
    try:
        run("git", "rm", "-q", f".github/workflows/{WORKFLOW}", cwd=dest)
        run("git", "commit", "-q", "-m", "Remove init workflow", cwd=dest)
        run("git", "push", "-q", cwd=dest)
    except subprocess.CalledProcessError:
        print(f"warning: couldn't remove .github/workflows/{WORKFLOW}; delete it by hand", file=sys.stderr)

    if not args.no_build:
        run("make", "build", cwd=dest)
        run("make", "pycharm", cwd=dest)

    print(f"\ndone: https://github.com/{full} cloned to {dest}")
    print(f"PyCharm: add a Docker interpreter on image {values['name']}:dev named "
          f"'{values['name']} docker', then fill DOPPLER_TOKEN in the 'handler' run config.")


if __name__ == "__main__":
    main()
