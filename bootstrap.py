"""Create a new repo that runs in Docker with uv and Doppler.

Usage: python bootstrap.py [CONFIG.toml] [--name ... --python ... --doppler-project ... --doppler-config ...] [--dest DIR]
Flags override values from the config file.
"""
import argparse
import re
import subprocess
import tomllib
from pathlib import Path
from string import Template

TEMPLATES = Path(__file__).parent / "templates"
DEFAULT_VERSIONS = {"uv": "0.11.1", "doppler": "3.77.1"}
# Flag name -> (config section, key, allowed pattern).
FIELDS = {
    "name": ("project", "name", r"[a-z][a-z0-9-]*"),
    "python": ("project", "python", r"3\.\d+"),
    "doppler_project": ("doppler", "project", r"[A-Za-z0-9_-]+"),
    "doppler_config": ("doppler", "config", r"[A-Za-z0-9_-]+"),
}


def load_values(config: Path | None, overrides: dict) -> dict:
    """Merge the config file with flag overrides, validate, and flatten into template variables."""
    cfg = tomllib.loads(config.read_text(encoding="utf-8")) if config else {}
    values, problems = {}, []
    for field, (section, key, pattern) in FIELDS.items():
        value = overrides.get(field) or cfg.get(section, {}).get(key)
        if not value:
            problems.append(f"missing {section}.{key} (--{field.replace('_', '-')})")
        elif not re.fullmatch(pattern, str(value)):
            problems.append(f"{section}.{key} must match {pattern}: {value!r}")
        else:
            values[field] = str(value)
    if problems:
        raise SystemExit("\n".join(problems))
    versions = DEFAULT_VERSIONS | cfg.get("versions", {})
    return values | {
        "package": values["name"].replace("-", "_"),
        "uv_version": versions["uv"],
        "doppler_version": versions["doppler"],
    }


def render(dest: Path, values: dict) -> list[Path]:
    """Copy every template into dest, substituting $vars in paths and contents."""
    written = []
    for src in sorted(p for p in TEMPLATES.rglob("*") if p.is_file()):
        rel = Template(src.relative_to(TEMPLATES).as_posix()).substitute(values)
        out = dest / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        text = Template(src.read_text(encoding="utf-8")).substitute(values)
        out.write_text(text, encoding="utf-8", newline="\n")
        written.append(out)
    return written


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("config", type=Path, nargs="?")
    for field in FIELDS:
        ap.add_argument(f"--{field.replace('_', '-')}", dest=field)
    ap.add_argument("--dest", type=Path, help="defaults to ./<name>")
    ap.add_argument("--no-git", action="store_true", help="skip git init (e.g. rendering into an existing repo)")
    args = ap.parse_args()

    values = load_values(args.config, {f: getattr(args, f) for f in FIELDS})
    dest = args.dest or Path.cwd() / values["name"]
    if dest.exists() and any(dest.iterdir()):
        raise SystemExit(f"{dest} exists and is not empty")

    written = render(dest, values)
    if not args.no_git:
        subprocess.run(["git", "init", "-q", str(dest)], check=True)
    print(f"created {dest} ({len(written)} files), "
          f"doppler {values['doppler_project']}/{values['doppler_config']}")


if __name__ == "__main__":
    main()
