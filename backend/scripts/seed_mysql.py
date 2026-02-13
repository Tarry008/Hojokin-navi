#!/usr/bin/env python
"""Seed Cloud SQL MySQL for hojokin-navi."""

import json
from pathlib import Path
import mysql.connector
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env
env_path = Path(__file__).parents[1] / ".env"
load_dotenv(env_path)

# Database configuration (from .env)
cfg = {
    "user": os.getenv("CLOUDSQL_USER", "root"),
    "password": os.getenv("CLOUDSQL_PASSWORD", "defaultpassword"),
    "host": os.getenv("CLOUDSQL_HOST", "127.0.0.1"),
    "port": int(os.getenv("CLOUDSQL_PORT", "3307")),
    "database": os.getenv("CLOUDSQL_DATABASE", "hojokin_db"),
    "charset": "utf8mb4",
    "use_unicode": True,
}
TARGET_MUNICIPALITY = "港区"

'''
# Create database if not exists
try:
    conn_no_db = mysql.connector.connect(
        user=cfg["user"],
        password=cfg["password"],
        host=cfg["host"],
        port=cfg["port"],
        charset=cfg["charset"],
        use_unicode=cfg["use_unicode"],

    )
    cur = conn_no_db.cursor()
    cur.execute(
        f"CREATE DATABASE IF NOT EXISTS {cfg['database']} "
        "DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
    )
    cur.close()
    conn_no_db.close()
    print(f"Database {cfg['database']} created/verified.")
except Exception as e:
    print(f"Failed to create database: {e}")
'''


# Connect to database
try:
    conn = mysql.connector.connect(**cfg)
    cur = conn.cursor()

    # Create table if not exists
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS programs (
        program_id VARCHAR(255) PRIMARY KEY,
        program_name TEXT,
        municipality VARCHAR(255),
        summary TEXT,
        eligibility JSON,
        deadline DATE,
        gray_zone_guidance JSON,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    cur.execute(create_table_sql)
    cur.execute("ALTER TABLE programs CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    print("Table 'programs' created/verified.")

    # Load seed data
    data_path = Path(__file__).parents[1] / "data" / "seed_programs.json"
    if not data_path.exists():
        raise FileNotFoundError(f"seed_programs.json not found at {data_path}")

    data = json.loads(data_path.read_text(encoding="utf-8"))

    # Insert/update programs
    insert_sql = """
    INSERT INTO programs (program_id, program_name, municipality, summary, eligibility, deadline, gray_zone_guidance)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        program_name = VALUES(program_name),
        municipality = VALUES(municipality),
        summary = VALUES(summary),
        eligibility = VALUES(eligibility),
        deadline = VALUES(deadline),
        gray_zone_guidance = VALUES(gray_zone_guidance)
    """

    cur.execute("DELETE FROM programs WHERE municipality <> %s", (TARGET_MUNICIPALITY,))

    for program in data:
        program_id = program.get("program_id", "")
        program_name = program.get("program_name", "")
        municipality = program.get("municipality", "")
        if municipality != TARGET_MUNICIPALITY:
            print(f"  Skipped (unsupported municipality): {program_id}")
            continue
        summary = program.get("summary", "")
        eligibility = json.dumps(program.get("eligibility", {}), ensure_ascii=False)
        
        # Parse deadline (YYYY-MM-DD or None)
        deadline_str = program.get("deadline")
        deadline = None
        if deadline_str:
            try:
                deadline = datetime.fromisoformat(deadline_str).date()
            except (ValueError, TypeError):
                pass

        gray_zone_guidance = json.dumps(program.get("gray_zone_guidance", []), ensure_ascii=False)

        try:
            cur.execute(insert_sql, (
                program_id,
                program_name,
                municipality,
                summary,
                eligibility,
                deadline,
                gray_zone_guidance,
            ))
            print(f"  Inserted/updated: {program_id}")
        except Exception as e:
            print(f"  Error inserting {program_id}: {e}")

    conn.commit()
    print(f"\nSuccessfully seeded {len(data)} programs.")

except Exception as e:
    print(f"Error during seeding: {e}")
    raise
finally:
    try:
        if cur:
            cur.close()
    except Exception:
        pass
    try:
        if conn:
            conn.close()
    except Exception:
        pass
