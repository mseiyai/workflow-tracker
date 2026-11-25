import argparse
import subprocess
import sys
from pathlib import Path, PurePosixPath


def is_disallowed_environment_file(path: str) -> bool:
    basename = PurePosixPath(path).name
    return basename == ".env" or (
        basename.startswith(".env.") and basename != ".env.example"
    )


def tracked_files(repository: Path) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "-C", str(repository), "ls-files", "-z"],
            capture_output=True,
            check=True,
            text=True,
        )
    except (OSError, subprocess.SubprocessError, UnicodeError):
        raise RuntimeError("Unable to inspect tracked files with Git.") from None

    return [path for path in result.stdout.split("\0") if path]


def parse_arguments(arguments: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    return parser.parse_args(arguments)


def main(arguments: list[str] | None = None) -> int:
    options = parse_arguments(arguments)

    try:
        paths = tracked_files(options.repo)
    except RuntimeError as error:
        print(error, file=sys.stderr)
        return 1

    disallowed_files = sorted(
        path for path in paths if is_disallowed_environment_file(path)
    )
    if disallowed_files:
        print("Tracked environment files are not allowed:", file=sys.stderr)
        for path in disallowed_files:
            print(path, file=sys.stderr)
        return 1

    print("Tracked environment file check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
