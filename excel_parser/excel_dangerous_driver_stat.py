from datetime import datetime
import re

import pandas as pd

from sql.queries import fetch_driver_data, insert_query


def upload_etas_dangerous_driver_stats(df: pd.DataFrame, conn, companyId: int, yearMonth: str):
    # 병합 해제 코드
    df.iloc[0] = df.iloc[0].ffill()
    formatted_date = datetime.strptime(yearMonth, "%Y-%m").date()
    
    df.columns = [f"{str(main).strip()}{str(sub).strip()}" if pd.notna(sub) else str(main).strip() for main, sub in zip(df.iloc[0], df.iloc[1])]
    df[["이름","코드"]] = df["운전자"].str.extract(r"(.+)\((.+)\)")
    df.drop(columns=["운전자"], inplace=True)
    df = df[["이름", "코드"] + [col for col in df.columns if col not in ["이름", "코드"]]]
    
    driver_df = fetch_driver_data(cursor=conn.cursor(), company_id=companyId)

    df.columns = df.columns.map(lambda x: re.sub(r"\s*\([^)]*\)\s*", "", x).strip())
    
    print(df.columns)
    
    for _, row in df.iterrows():
        selected_driver_id = row['코드']
        selected_driver = driver_df[driver_df["emp_no"] == selected_driver_id]
        if not selected_driver.empty :
            driver_primary_id = int(selected_driver["id"].iloc[0])
            print(driver_primary_id)
            query = insert_query("dangerous_driving_stat", "driver_id", "report_year_month", "danger_degree", 
                                 "major_danger_behavior", "maximum_driving_time", "sum_dangerous_driving_stat_per_100", 
                                 "speeding_count", "speeding_time", "long_speeding_count", "long_speeding_time", 
                                 "rapid_accel", "rapid_start", "rapid_decel", "sudden_stop", 
                                 "sharp_turn_left", "sharp_turn_right", "sharp_uturn", 
                                 "sudden_overtake", "sudden_lane_change", "driving_days", 
                                 "driving_distance", "driving_time")
            conn.cursor().execute(query, (driver_primary_id, formatted_date, row["위험수준"],
                                          row["주요위험운전행동"], row["최대연속운전"], row["100km당위험운전행동합계"],
                                          row["과속건수"], row["과속시간"], row["장기과속건수"], row["장기과속시간"],
                                          row["급가속"], row["급출발"], row["급감속"], row["급정지"],
                                          row["급회전좌회전"], row["급회전우회전"], row["급회전U턴"],
                                          row["급앞지르기"], row["급진로변경"], row["운행정보일수"],
                                          row["운행정보거리"], row["운행정보시간"]))
    
    conn.commit()
    conn.cursor().close()
    
    return None