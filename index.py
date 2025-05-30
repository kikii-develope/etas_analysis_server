import os
import uvicorn
from config.environment import get_env
from crawler.crawler_etas import get_dangerous_driver_report_list, init_driver, is_change_password_page, login
from models.etas_login_request import EtasLoginRequest
from sql.index import connect_to_mysql
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

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
        return {"message": "Login successful", "status": 200, "object": driver.current_url}
    except Exception as e:
        raise HTTPException(status_code=400, detail={
            "message": "Login failed",
            "error": str(e),
            "status": 400
        })
    
@app.get("/etas-page/current-page")
def get_page():
    driver = init_driver()
    return {"message": "Current page", "status": 200, "object": is_change_password_page(driver)}

def main():
    # env = get_env()
    # print(env)
    
    host = "168.126.147.134"
    user = "root"
    password = "1733a-sql"
    database = "etas-data"
    port = 13306
    
    conn = connect_to_mysql(host=host, user=user, password=password, database=database, port=port)
    
    # driver = login("bybus", "**sam00831");
    # print(driver)
    # input("Press Enter to continue...")
    
    # get_dangerous_driver_report_list(conn, "bybus", "**sam00831", "2024-10", 2)
    
    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)