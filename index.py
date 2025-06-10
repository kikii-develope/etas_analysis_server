from contextlib import asynccontextmanager
import io
import os
import time
import pandas as pd
import uvicorn
from config.environment import get_env
from crawler.crawler_etas import download_pdf_file, download_pdf_files, get_dangerous_driver_report_list, init_driver, is_change_password_page, login
from crawler.session_utils import check_jsessionid
from excel_parser.excel_dangerous_driver_stat import upload_etas_dangerous_driver_stats
from excel_parser.excel_driver_info import upload_etas_driver_data
from models.etas_login_request import EtasLoginRequest
from sql.index import connect_to_mysql
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware


db_conn = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_conn
    
    host = "168.126.147.134"
    user = "root"
    password = "1733a-sql"
    database = "kiki-dev-v2"
    port = 13307

    
    
    db_conn = connect_to_mysql(host=host, user=user, password=password, database=database, port=port)
    
    yield
    if db_conn is not None:
        db_conn.close()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.post("/etas-login")
async def etas_login(req: EtasLoginRequest):
    try:
        driver = await login(req.id, req.password);
        
        time.sleep(5)
        
        await download_pdf_files(db_conn, driver, req.companyId, req.yearMonth, req.riskLevel)
        
        return {"message": "Login successful", "status": 200, "object": driver.current_url}
    except Exception as e:
        print(e.with_traceback())
        raise HTTPException(status_code=400, detail={
            "message": "Login failed",
            "error": str(e),
            "status": 400
        })
        
@app.post("/etas/upload-driver-data")
async def get_etas_driver_data(file: UploadFile = File(...), companyId: int = Form(...)):
    try:
        filename = file.filename
        file_content = await file.read()
        ext = os.path.splitext(filename)[-1].lower()
        
        if ext == ".xlsx" or ext == ".xls":
            df = pd.read_excel(io.BytesIO(file_content), header=0)
        elif ext == ".csv":
            df = pd.read_csv(io.StringIO(file_content), sep="\t", header=0)
        else:
            raise HTTPException(status_code=400, detail={
                "message": "Invalid file type",
                "error": "Only .xlsx and .csv files are supported",
                "status": 400
            })
        
        upload_etas_driver_data(df, db_conn, companyId)
        
        return {"message": "Upload successful", "status": 200}
        
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail={
            "message": "Upload failed",
            "error": str(e),
            "status": 400
        })
        

@app.post("/etas/upload-driving-data")
async def get_etas_driving_data(file: UploadFile = File(...), companyId: int = Form(...), yearMonth: str = Form(...)):
    try:
        print(file)
        print(companyId)
        print(yearMonth)
        filename = file.filename
        file_content = await file.read()
        ext = os.path.splitext(filename)[-1].lower()
        
        if ext == ".xlsx" or ext == ".xls":
            df = pd.read_excel(io.BytesIO(file_content), header=0)
        elif ext == ".csv":
            df = pd.read_csv(io.StringIO(file_content), sep="\t", header=0)
        else:
            raise HTTPException(status_code=400, detail={
                "message": "Invalid file type",
                "error": "Only .xlsx and .csv files are supported",
                "status": 400
            })
        
        upload_etas_dangerous_driver_stats(df, db_conn, companyId, yearMonth)
        
        return {"message": "Upload successful", "status": 200}
        
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail={
            "message": "Upload failed",
            "error": str(e),
            "status": 400
        })

@app.post("/etas/download-dangerous-driver-report")
async def download_dangerous_driver_report(requst: Request):
    try:
        data = await requst.json()
        company_id = data.get("companyId")
        year_month = data.get("yearMonth")
        emp_no = data.get("empNo")
        
        print(company_id)
        print(year_month)
        print(emp_no)
        
        download_pdf_file(db_conn, company_id, emp_no, year_month=year_month)
        
        return {"message": "Download successful", "status": 200}
    except HTTPException as e:
        raise e
    except Exception as e:
        print(e.with_traceback())
        raise HTTPException(status_code=400, detail={
            "message": "Download failed",
            "error": str(e),
            "status": 400
        })
    
    

def main():
    # env = get_env()
    # print(env)
    
    host = "168.126.147.134"
    user = "root"
    password = "1733a-sql"
    database = "kiki-dev-v2"
    port = 13307
    
    conn = connect_to_mysql(host=host, user=user, password=password, database=database, port=port)
    
    # driver = login("bybus", "**sam00831");
    # print(driver)
    # input("Press Enter to continue...")
    
    # get_dangerous_driver_report_list(conn, "bybus", "**sam00831", "2024-10", 2)
    

if __name__ == "__main__":
    
    uvicorn.run(app, host="0.0.0.0", port=8000)