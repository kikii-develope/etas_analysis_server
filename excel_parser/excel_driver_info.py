import pandas as pd
from excel_parser.excel_uploader import trim_df
from sql.queries import fetch_driver_data, insert_query


def upload_etas_driver_data (df: pd.DataFrame, conn,  companyId: int):

    table_data = fetch_driver_data(conn.cursor(), companyId);
    
    print(table_data)

    df = trim_df(df, *["운전자명", "운전자코드", "등록일"])
    
    if "운전자명" not in df.columns:
        raise ValueError(f"컬럼 '운전자명'이 존재하지 않습니다.")
    
    df[["이름","이름(코드)"]] = df["운전자명"].str.extract(r"(.+)\((.+)\)")
    df.drop(columns=["운전자명"], inplace=True)
    
    df_diff = df[df["운전자코드"] != df["이름(코드)"]]
    
    df_filtered = df[~df.index.isin(df_diff.index)]
    query = insert_query("etas_driver", "company_id", "emp_no", "name", "registration_date")
    for index, row in df_filtered.iterrows():
        exist = table_data[(table_data["emp_no"] == row["운전자코드"]) & (table_data["name"] == row["이름"]) & (table_data["company_id"] == companyId)]
        if exist.empty:
            conn.cursor().execute(query, (companyId, row["운전자코드"], row["이름"], row["등록일"]))
    
    conn.commit()
    conn.cursor().close()