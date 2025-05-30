import mysql.connector

def connect_to_mysql(host: str, user: str, password: str, database: str, port: int):
    """MySQL에 연결하는 함수"""
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port
        )
        print("✅ MySQL 연결 성공")
        return conn
    except mysql.connector.Error as e:
        print(f"❌ MySQL 연결 실패: {e}")
        return None