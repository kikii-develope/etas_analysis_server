# 테이블에 값 삽입 쿼리문
import pandas as pd

def insert_query (table: str, *cols: str) -> str:
    base_query = "INSERT INTO "
    base_query += table + " ("
    for _, col in enumerate(cols):
        if _ == len(cols) - 1:
            base_query += col
        else :
            base_query += col + ", "
    base_query += ") VALUES ("
    for _, col in enumerate(cols):
        if _ == len(cols) - 1:
            base_query += "%s"
        else :
            base_query += "%s, "
    base_query += ")"
    
    return base_query

# etas 운전자 데이터 불러오기(company_id 필요)
def fetch_driver_data (cursor, company_id):
    query = f"SELECT id, emp_no, name FROM driver WHERE company_id = {company_id}"
    cursor.execute(query)
    result = cursor.fetchall()

    return pd.DataFrame(result, columns=["id", "emp_no", "name"])