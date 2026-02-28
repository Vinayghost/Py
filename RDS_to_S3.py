import pymysql
import boto3
import subprocess
import os
from datetime import datetime

# AWS Credentials
AWS_ACCESS_KEY = "AKIAZQ3DO7MIWQ2ERLIL"
AWS_SECRET_KEY = "sdZSnUrQ6b/eH/uNdK1cv1XsXlqq7HTlcmwkfjn/"
AWS_REGION = "ap-south-1"

# RDS MySQL Configuration
RDS_HOST = "your-rds-endpoint.rds.amazonaws.com"
RDS_USER = "admin"
RDS_PASSWORD = "yourpassword"
RDS_DATABASE = "yourdatabase"

# S3 Configuration
S3_BUCKET_NAME = "your-s3-bucket"
BACKUP_FILE = f"rds_backup_{datetime.now().strftime('%Y%m%d%H%M%S')}.sql"

def connect_rds():
    try:
        connection = pymysql.connect(
            host=RDS_HOST,
            user=RDS_USER,
            password=RDS_PASSWORD,
            database=RDS_DATABASE,
            cursorclass=pymysql.cursors.DictCursor
        )
        print("Connected to RDS")
        return connection
    except Exception as e:
        print(f"RDS Connection Failed: {e}")
        return None

def create_table():
    connection = connect_rds()
    if connection:
        try:
            with connection.cursor() as cursor:
                create_table_query = """
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100),
                    email VARCHAR(100) UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
                cursor.execute(create_table_query)
                connection.commit()
                print("Table 'users' created successfully")
        except Exception as e:
            print(f"Table Creation Failed: {e}")
        finally:
            connection.close()

def backup_rds_to_s3():
    try:
        # Backup command using mysqldump
        backup_command = f"mysqldump -h {RDS_HOST} -u {RDS_USER} -p{RDS_PASSWORD} {RDS_DATABASE} > {BACKUP_FILE}"
        subprocess.run(backup_command, shell=True, check=True)
        print(f"Database backup created: {BACKUP_FILE}")

        # Upload to S3 with credentials
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            region_name=AWS_REGION
        )
        s3_client.upload_file(BACKUP_FILE, S3_BUCKET_NAME, BACKUP_FILE)
        print(f"Backup uploaded to S3: s3://{S3_BUCKET_NAME}/{BACKUP_FILE}")

        # Remove local backup file
        os.remove(BACKUP_FILE)
    except Exception as e:
        print(f"Backup Failed: {e}")

if __name__ == "__main__":
    create_table()
    backup_rds_to_s3()