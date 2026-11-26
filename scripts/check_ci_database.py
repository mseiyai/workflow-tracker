import os
import sys

from sqlalchemy.exc import ArgumentError
from sqlalchemy.engine import URL, make_url


DATABASE_VARIABLES = ("DATABASE_URL", "TEST_DATABASE_URL")


def validation_error(variable_name: str, message: str) -> ValueError:
    return ValueError(f"{variable_name} {message}")


def validate_database_url(variable_name: str, value: str | URL | None) -> None:
    if value is None or (isinstance(value, str) and not value.strip()):
        raise validation_error(variable_name, "must be set")

    try:
        url = make_url(value)
    except (ArgumentError, TypeError, ValueError):
        raise validation_error(
            variable_name, "is not a valid PostgreSQL URL"
        ) from None

    if url.get_backend_name() != "postgresql":
        raise validation_error(variable_name, "is not a valid PostgreSQL URL")

    # Driver query options can override the database selected by the URL path.
    if url.query:
        raise validation_error(variable_name, "must not include query options")

    if url.database is None or not url.database.endswith("_test"):
        raise validation_error(
            variable_name, "database name must end in '_test'"
        )


def main() -> int:
    try:
        for variable_name in DATABASE_VARIABLES:
            validate_database_url(variable_name, os.environ.get(variable_name))
    except ValueError as error:
        print(error, file=sys.stderr)
        return 1

    print("CI database contract OK.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
