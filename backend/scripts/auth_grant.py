import os
import mysql.connector
from google.cloud import secretmanager
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parents[1] / ".env"
load_dotenv(env_path)

cfg = {
    "project_id": os.getenv("GCP_PROJECT_ID"),
    "secret_id": os.getenv("GCP_SECRET_ID"), 
}

def get_secret(project_id, secret_id):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")


try:
    password = get_secret(cfg["project_id"], cfg["secret_id"])
    print(password)
    config = {
        'user': 'backend_user',
        'password': password,
        'host': '127.0.0.1',
        'port': 3306,
        'database': 'hojokin_db',
        'auth_plugin': 'mysql_native_password' 
    }

    print("Connecting as 'backend_user'...")
    cnx = mysql.connector.connect(**config)
    cursor = cnx.cursor()
    
    # 1. 実際にDBに登録されているIAMユーザーの正確な名前とホストを取得
    print("Finding exact IAM user string...")
    cursor.execute("SELECT user, host FROM mysql.user WHERE user LIKE 'youkey0505%';")
    rows = cursor.fetchall()
    
    if not rows:
        print("Error: IAM user not found in MySQL. Please check 'gcloud sql users list'.")
    else:
        for user_name, host_name in rows:
            print(f"Target found: '{user_name}'@'{host_name}'")
            # 2. 取得した正確な名前に対してGRANTを実行
            try:
                # 引用符でしっかり囲んで実行
                grant_sql = f"GRANT ALL PRIVILEGES ON hojokin_db.* TO '{user_name}'@'{host_name}';"
                cursor.execute(grant_sql)
                print(f"Successfully granted privileges to '{user_name}'@'{host_name}'")
            except mysql.connector.Error as e:
                print(f"Failed to grant to this user: {e}")

        cursor.execute("FLUSH PRIVILEGES;")
        print("Finalizing changes...")

    cursor.close()
    cnx.close()
    print("Done.")

except Exception as err:
    print(f"Error occurred: {err}")