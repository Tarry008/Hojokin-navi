from __future__ import annotations

import json
from datetime import date, datetime
from typing import Any, List, Optional

from ..models import Program


class MySQLStore:
    def __init__(
        self,
        host: str,
        port: int,
        unix_socket: Optional[str],
        user: str,
        password: str,
        database: str,
        connect_timeout: int = 5,
    ):
        try:
            import mysql.connector  # type: ignore
        except Exception as exc:
            raise RuntimeError("mysql-connector-python is not available") from exc

        self._mysql = mysql.connector
        self._conn_cfg = {
            "user": user,
            "password": password,
            "database": database,
            "connection_timeout": connect_timeout,
            "charset": "utf8mb4",
            "use_unicode": True,
        }
        if unix_socket:
            self._conn_cfg["unix_socket"] = unix_socket
        else:
            self._conn_cfg["host"] = host
            self._conn_cfg["port"] = port

    def list_programs(self, municipality: Optional[str] = None) -> List[Program]:
        sql = """
        SELECT
            program_id,
            program_name,
            municipality,
            summary,
            eligibility,
            deadline,
            gray_zone_guidance
        FROM programs
        """
        params: List[Any] = []
        if municipality:
            sql += " WHERE municipality = %s"
            params.append(municipality)

        rows = self._fetch_all(sql, params)
        return [self._row_to_program(row) for row in rows]

    def get_program(self, program_id: str) -> Optional[Program]:
        sql = """
        SELECT
            program_id,
            program_name,
            municipality,
            summary,
            eligibility,
            deadline,
            gray_zone_guidance
        FROM programs
        WHERE program_id = %s
        LIMIT 1
        """
        row = self._fetch_one(sql, [program_id])
        if not row:
            return None
        return self._row_to_program(row)

    def _fetch_all(self, sql: str, params: List[Any]) -> List[dict]:
        conn = self._mysql.connect(**self._conn_cfg)
        try:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(sql, params)
                return cursor.fetchall() or []
            finally:
                cursor.close()
        finally:
            conn.close()

    def _fetch_one(self, sql: str, params: List[Any]) -> Optional[dict]:
        conn = self._mysql.connect(**self._conn_cfg)
        try:
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute(sql, params)
                return cursor.fetchone()
            finally:
                cursor.close()
        finally:
            conn.close()

    def _row_to_program(self, row: dict) -> Program:
        deadline = row.get("deadline")
        if isinstance(deadline, (date, datetime)):
            deadline_value = deadline.isoformat()
        else:
            deadline_value = deadline

        payload = {
            "program_id": row.get("program_id", ""),
            "program_name": row.get("program_name", ""),
            "municipality": row.get("municipality", ""),
            "summary": row.get("summary", ""),
            "eligibility": _parse_json_value(row.get("eligibility"), {}),
            "deadline": deadline_value,
            "gray_zone_guidance": _parse_json_value(row.get("gray_zone_guidance"), []),
        }
        return Program.model_validate(payload)


def _parse_json_value(value: Any, default: Any) -> Any:
    if value is None:
        return default
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, (bytes, bytearray)):
        value = value.decode("utf-8")
    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception:
            return default
    return default
