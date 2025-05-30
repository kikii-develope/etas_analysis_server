import pandas as pd
from typing import Literal
import re
from datetime import datetime

from sql.queries import insert_query

def load_excel(file_path: str, extension: Literal["xls", "xlsx"]):
    excel_engine = ""
    if ( extension == 'xls' ): 
        excel_engine = 'xlrd'
    elif( extension == 'xlsx' ):
        excel_engine = 'openpyxl'
    else:
        raise Exception("확장자명이 정확하지 않습니다.")
    try:
        df = pd.read_excel(file_path, engine=excel_engine)
        print("✅ 엑셀 파일 로드 성공")
        return df
    except Exception as e:
        print(f"❌ 엑셀 파일 로드 실패: {e}")
        return None
    
def find_header_row (df: pd.DataFrame, cols: list[str]):
    for i, row in df.iterrows():
        row_values = ["".join(str(value).split()) for value in row.values]
        if all(value in row_values for value in cols):
            return i
    return None

def trim_df(df: pd.DataFrame, *cols: str):
    header_index = find_header_row(df, cols)
    
    #헤더가 되는 위치 위의 값들 모두 정리.
    trimed_df = df.iloc[header_index:].reset_index(drop=True)
    
    #컬럼의 값 전체가 nan 인 컬럼 없애기
    trimed_df = trimed_df.dropna(axis=1, how='all')
    trimed_df.columns = trimed_df.iloc[0]
    return trimed_df