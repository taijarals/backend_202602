import os
import psycopg2
from psycopg2.extras import RealDictCursor
from providers.base import DatabaseProvider


class SQLProvider(DatabaseProvider):
    def __init__(self):
        self.connection_string = os.getenv(
            "DATABASE_URL", 
            "postgresql://postgres:%40Ravi0072006@db.iarzavoeakzlblihucnt.supabase.co:5432/postgres"
        )

    def _get_conn(self):
        return psycopg2.connect(
            self.connection_string, 
            cursor_factory=RealDictCursor
        )

    def fetch_all(self, query, params=None):
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params or {})
                return [dict(row) for row in cur.fetchall()]

    def fetch_one(self, query, params=None):
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params or {})
                res = cur.fetchone()
                return dict(res) if res else None

    def execute(self, query, params=None):
        with self._get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params or {})
            conn.commit()
        return True