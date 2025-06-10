
import os
import re
import time

from fastapi import HTTPException
import pandas as pd
import urllib
from crawler.etas_company_info import ETAS_COMPANY_INFO
from crawler.index import get_default_download_path, load_web_driver
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from requests_toolbelt import MultipartEncoder
import requests


def start_driver(user_data_dir: str = None):
    driver = load_web_driver(user_data_dir)
    print("new Driver Started")
    return driver

def init_driver():
    driver = start_driver()
    return driver
        
def check_session_id(driver):
    try:
        if driver is None:
            return False
        cookies = driver.get_cookies()
        for cookie in cookies:
            if cookie['name'] == 'JSESSIONID':
                return True
        return False
    except Exception as e:
        print(e)
        return False

def wait_for_element(driver, by, value, timeout=10):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, value))
    )

async def login(id: str, password: str):
    try:
        driver = init_driver()
        
        driver.get("https://tsum.kotsa.or.kr/tsum/mbs/inqFrmLogin.do?mobileGubun=PC");
        
        try:
            #1차 시도
            wait_for_element(driver, By.ID, "id")
        except TimeoutException:
            print("1차 시도 실패. 새로고침 후 재요청", flush=True)
            driver.refresh()
            try:
                #2차 시도
                wait_for_element(driver, By.ID, "id")
            except TimeoutException:
                driver.quit()
                raise TimeoutException("로그인 페이지를 찾을 수 없습니다.")
        
        input_id = driver.find_element(By.ID, "id")
        input_id.send_keys(id)
        
        input_password = driver.find_element(By.ID, "passwd")
        input_password.send_keys(password)
        input_password.send_keys(Keys.RETURN)
        time.sleep(2)
        
        if not await find_is_login_symbol(driver):
            print("로그인에 실패했습니다. 다시 시도해주세요.", flush=True)
            driver.quit()
            raise Exception("로그인에 실패했습니다.")
        
        return driver
    except Exception as e:
        print(e.with_traceback())
        raise

async def find_is_login_symbol (driver):
    print("find_is_login_symbol", flush=True)
    is_change_pw_page = await is_change_password_page(driver)
    if is_change_pw_page:
        return True
    
    driver.get("https://etas.kotsa.or.kr/main.do?emailRecvYn=Y")
    
    time.sleep(3)
    
    try:
        driver.find_element(By.TAG_NAME, "html")
        driver.find_element(By.TAG_NAME, "body")
        driver.find_element(By.ID, "wrap")
        driver.find_element(By.ID, "header_wrap")
        header_div = driver.find_element(By.ID, "header")
        
        return "로그아웃" in header_div.get_attribute("outerHTML")
    except NoSuchElementException:
        print("로그인에 실패하였습니다.", flush=True)
        return False

async def is_change_password_page(driver):
    base_url_regex = "kotsa.or.kr"
    current_url = driver.current_url
    
    print(current_url, flush=True)
    if base_url_regex in current_url:
        if "pwrdChange" in current_url: # 비밀번호 변경 페이지인지 확인 후, 메인화면으로 이동.
            driver.execute_script("fnNextChange();")
            time.sleep(2)
            driver.execute_script("window.location.href='https://etas.kotsa.or.kr/sso/CreateRequest.jsp?RelayState=/sso/ssoLogin.jsp'")
            return True 
        else:
            return False
    else:
        return False

def get_dangerous_driver_list (conn, year_month, company_id):
    cursor = conn.cursor()
    
    query = f"SELECT d.emp_no, dda.* FROM dangerous_driving_stat dda INNER JOIN driver d ON d.id = dda.driver_id WHERE d.company_id = {company_id} AND dda.report_year_month = '{year_month + "-01"}' AND dda.danger_degree = '매우위험'"
    cursor.execute(query)
    
    result = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    cursor.close()
    return pd.DataFrame(result, columns=columns)

async def download_pdf_files(conn, driver, company_id, year_month, risk_level):
    cursor = conn.cursor()
    query = f"SELECT * FROM dangerous_driving_stat dds INNER JOIN etas_driver ed ON dds.driver_id = ed.id WHERE ed.company_id = {company_id} AND dds.report_year_month = '{year_month}' AND dds.danger_degree = '{risk_level}'"
    cursor.execute(query)
    result = cursor.fetchall()
    columns = [col[0] for col in cursor.description]
    cursor.close()
    df = pd.DataFrame(result, columns=columns)
    
    for index, row in df.iterrows():
        #이미 저장된 종합진단표가 있는 경우 
        if row['file_url'] is not None:
            continue
        await download_pdf_file(conn, driver, company_id, row['emp_no'], year_month, row['driver_id'])

async def download_pdf_file(conn, driver, company_id, emp_no, year_month, driver_id):
    try:
        first_encoding = urllib.parse.quote(emp_no)
        second_encoding = urllib.parse.quote(first_encoding)
        
        search_transco_cd = ETAS_COMPANY_INFO[int(company_id)]['transCoCd']
        search_transco_nm = ETAS_COMPANY_INFO[int(company_id)]['transCoNm']
        year = year_month.split('-')[0]
        month = year_month.split('-')[1]
        driver_emp_no = emp_no
        
        search_transco_nm = urllib.parse.quote(search_transco_nm)
        
        url = f'https://etas.kotsa.or.kr/etas/frtb0202/pop2/goNewView.do?searchYyyy={year}&searchMm={month}&searchTranscoCd={search_transco_cd}&searchTranscoNm={search_transco_nm}&searchDrivrCd={second_encoding}'
        driver.execute_script(f"window.open('{url}', '_blank');")
        time.sleep(2)
        driver.switch_to.window(driver.window_handles[1])
        
        frmElement = driver.find_element(By.ID, "frmReport")
        
        if frmElement is None:
            driver.close()
            raise Exception(f"Timeout:: {driver_emp_no}번 승무원 정보를 찾을 수 없습니다.")

        # iframe_element = driver.find_element(By.ID, "frmReport")
        driver.switch_to.frame(frmElement)
        driver.execute_script("do_report()")

        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "html")))
        except TimeoutException:
            print(f"Timeout:: iframe 정보를 찾을 수 없습니다.")
            raise Exception(f"Timeout:: iframe 정보를 찾을 수 없습니다.")
            
        inner_html_element = driver.find_element(By.TAG_NAME, "html")
        inner_body_element = driver.find_element(By.TAG_NAME, "body")
        pop_diag_div = driver.find_element(By.ID, "pop-diagnosis")
        content_div = driver.find_element(By.ID, "content-01")
        top_btn = driver.find_element(By.CLASS_NAME, "page-btn").find_element(By.XPATH, "//a[@class='print' and @onclick='do_report()']")
        top_btn.click()

        time.sleep(1)
        
        driver.switch_to.window(driver.window_handles[-1])
        
        wait_for_element(driver, By.ID, "targetDiv1")
        driver.find_element(By.TAG_NAME, "div")
        driver.find_element(By.CLASS_NAME, "report_menu_div")
        driver.find_element(By.TAG_NAME, "tr")
        driver.find_element(By.CLASS_NAME, "report_menu_table_td")
        driver.find_element(By.CLASS_NAME, "report_menu_table_td_div")
        driver.find_element(By.TAG_NAME, "nobr")
        # report_top_btns = wait_for_element(driver, By.CLASS_NAME, 'report_menu_button')
        report_top_btns = driver.find_elements(By.CLASS_NAME, "report_menu_button")
        time.sleep(2)

        download_file_url = get_default_download_path()

        for index, report_top_btn in enumerate(report_top_btns):
            button_html = report_top_btn.get_attribute("outerHTML")
            if ("저장" in button_html and "PDF 저장" not in button_html):
                time.sleep(1)
                report_top_btn.click()
                time.sleep(1)
                driver.find_element(By.CLASS_NAME, "report_popup_view")
                file_box = driver.find_element(By.CLASS_NAME, "report_save_view_position")
                boxes = file_box.find_elements(By.TAG_NAME, "div")
                for idx, setting_box in enumerate(boxes):
                    if idx == 0:
                        select_element = setting_box.find_element(By.TAG_NAME, "select")
                        select = Select(select_element)
                        select.select_by_index(2)
                    elif idx == 1:
                        filename_input = setting_box.find_element(By.TAG_NAME, "input")
                        filename_input.clear()
                        filename_input.send_keys(driver_emp_no)
                    else:
                        break
                buttons = file_box.find_elements(By.TAG_NAME, "button")
                for i, button in enumerate(buttons):
                    if "저장" in button.get_attribute("outerHTML"):                        
                        button.click()
                        time.sleep(3)
                        
                        file_path = os.path.join(download_file_url, f'{driver_emp_no}.pdf')
                        print(file_path)
                            
                        res = await upload_pdf_file(year_month, driver_id, file_path)
                        if res is None:
                            print("upload failed")
                        elif(res['status'] == 200):
                            uploaded_file_path = res['object']['files'][0]['url']
                            
                            cursor = conn.cursor()
                            query = f"UPDATE dangerous_driving_stat SET file_url = '{uploaded_file_path}' WHERE driver_id = {driver_id} and report_year_month = '{year_month}'"
                            cursor.execute(query)
                            conn.commit()
                            cursor.close()
                        else:
                            print("upload failed")
                        initialize_driver_page(driver)
                        return driver
                
                initialize_driver_page(driver)
                return driver
            
            
    except WebDriverException as e:
        import traceback
        traceback.print_exc()
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise

#초기 페이지 상태로 돌려놓는 함수.
def initialize_driver_page(driver):
    
    # 현재 윈도우 핸들 목록
    handles = driver.window_handles

            # 첫 번째(0번) 탭만 남기고 뒤에 있는 탭을 모두 닫기
    while len(handles) > 1:
        # 마지막 탭으로 전환
        driver.switch_to.window(handles[-1])
        driver.close()  # 현재 탭 닫기

        # 남은 핸들 목록 갱신
        handles = driver.window_handles

        # 마지막 남은 탭으로 포커스
        driver.switch_to.window(handles[0])

# 파일명 처리 함수(윈도우 제약사항 고려)
def sanitize_filename(filename: str) -> str:
    # Windows에서 금지된 문자 목록: \ / : * ? " < > |
    return re.sub(r'[\\\/:*?"<>|]', '_', filename)    

def get_dangerous_driver_report_list (conn, login_id: str, password: str, year_month: str, company_id: int):
    driver = login(login_id, password)

    dangerous_driver_list = get_dangerous_driver_list(conn, year_month=year_month, company_id=company_id)
    dangerous_driver_emp_no_list = dangerous_driver_list["emp_no"].to_numpy()
    
    download_pdf_files(driver, dangerous_driver_emp_no_list)
    input("if press enter, i quit")
    driver.quit()


async def upload_pdf_file(year_month, driver_id, file_url):
    
    url = 'http://localhost:8989/s3/upload/multiple'
    data = {
        'bucketName': 'etas-dangerous-report',
        'path': f'{year_month}/{driver_id}',
    }
    file_path = file_url  # 실제 파일 경로
    file_name = os.path.basename(file_path)
    file_name = sanitize_filename(file_name)
    try:
        with open(file_path, "rb") as f:
            files = {
                "files": (file_name, f, "application/pdf")
            }
            response = requests.post(url, data=data, files=files)
            print(response.status_code, response.text)
    except Exception as e:
        print(e)
        return None
    return response.json()
    