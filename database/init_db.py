from pathlib import Path

from sqlalchemy import text

from database.db import engine


def initialize_database():

    schema_file = (
        Path(__file__)
        .parent
        / "schema.sql"
    )

    sql = schema_file.read_text()

    with engine.begin() as conn:

        for statement in sql.split(";"):

            statement = statement.strip()

            if statement:

                conn.execute(
                    text(statement)
                )

    print("Database initialized")


if __name__ == "__main__":
    initialize_database()