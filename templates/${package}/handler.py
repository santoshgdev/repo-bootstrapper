import os


def main() -> None:
    project, config = os.environ.get("DOPPLER_PROJECT"), os.environ.get("DOPPLER_CONFIG")
    print(f"${name}: running with Doppler {project}/{config}")


if __name__ == "__main__":
    main()
