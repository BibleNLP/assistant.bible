""" Test fixtures and stuff"""

import os
import shutil
import pytest
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


@pytest.fixture
def fresh_db():
    """For Chroma: Deletes the chroma test db folder if one existed
    For Postgres: Drops the test database if one existed
    Returns: the DB_config to be used for chroma or postgres connection"""
    collection_name = "adotdcollection_test"

    # Chroma Specific clean up
    chroma_db_path = "chromadb_store_test"
    if os.path.exists(chroma_db_path):
        shutil.rmtree(chroma_db_path)

    # Postgres specific cleanup
    pg_db_host = os.environ.get("POSTGRES_DB_HOST", "localhost")
    pg_db_port = os.environ.get("POSTGRES_DB_PORT", "5432")
    pg_db_user = os.environ.get("POSTGRES_DB_USER", "admin")
    pg_db_password = os.environ.get("POSTGRES_DB_PASSWORD", "secret")
    db_conn = psycopg2.connect(
        user=pg_db_user,
        password=pg_db_password,
        host=pg_db_host,
        port=pg_db_port,
        dbname="postgres",
    )
    db_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = db_conn.cursor()
    delete_statement = f"DROP DATABASE IF EXISTS {collection_name}"
    cur.execute(delete_statement)
    create_statement = f"CREATE DATABASE {collection_name}"
    cur.execute(create_statement)
    cur.close()
    db_conn.close()

    try:
        yield {"dbPath": chroma_db_path, "collectionName": collection_name}
    finally:
        if os.path.exists(chroma_db_path):
            shutil.rmtree(chroma_db_path)
        db_conn = psycopg2.connect(
            user=pg_db_user,
            password=pg_db_password,
            host=pg_db_host,
            port=pg_db_port,
            dbname="postgres",
        )
        db_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = db_conn.cursor()
        delete_statement = f"DROP DATABASE IF EXISTS {collection_name}"
        cur.execute(delete_statement)
        cur.close()
        db_conn.close()
