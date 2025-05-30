
import time

import pandas as pd
import urllib
from crawler.index import load_web_driver
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

driver = None

def init_driver():
    global driver
    if driver is None:
        driver = load_web_driver()
    return driver

def check_session_id(driver):
    if driver is None:
        return False
    cookies = driver.get_cookies()
    for cookie in cookies:
        if cookie['name'] == 'JSESSIONID':
            return True
    return False

def wait_for_element(by, value, timeout=10):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, value))
    )

async def login(id: str, password: str):
    driver = init_driver()
    
    if check_session_id(driver):
        return driver
    
    driver.get("https://tsum.kotsa.or.kr/tsum/mbs/inqFrmLogin.do?mobileGubun=PC");
    
    try:
        #1차 시도
        wait_for_element(By.ID, "id")
    except TimeoutException:
        print("1차 시도 실패. 새로고침 후 재요청", flush=True)
        driver.refresh()
        try:
            #2차 시도
            wait_for_element(By.ID, "id")
        except TimeoutException:
            raise TimeoutException("로그인 페이지를 찾을 수 없습니다.")
    
    input_id = driver.find_element(By.ID, "id")
    input_id.send_keys(id)
    
    input_password = driver.find_element(By.ID, "passwd")
    input_password.send_keys(password)
    input_password.send_keys(Keys.RETURN)
    time.sleep(2)
    
    if not await find_is_login_symbol(driver):
        print("로그인에 실패했습니다. 다시 시도해주세요.", flush=True)
        raise Exception("로그인에 실패했습니다.")
        
    return driver

async def find_is_login_symbol (driver):
    print("find_is_login_symbol", flush=True)
    is_change_pw_page = await is_change_password_page(driver)
    if is_change_pw_page:
        return True
    
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

def download_pdf_files(driver, driver_emp_no_list):
    for driver_emp_no in driver_emp_no_list:
        first_encoding = urllib.parse.quote(driver_emp_no)
        second_encoding = urllib.parse.quote(first_encoding)
        
        driver.get(f'https://etas.kotsa.or.kr/etas/frtb0202/pop2/goNewView.do?searchYyyy=2024&searchMm=10&searchTranscoCd=00461&searchTranscoNm=%EB%B3%B4%EC%98%81%EC%9A%B4%EC%88%98(%EC%A3%BC)(%EA%B5%AC%EB%B6%80%EA%B0%95%EA%B5%90%ED%86%B5)&searchDrivrCd={second_encoding}')
        
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "frmReport")))
        except TimeoutException:
            print(f"Timeout:: {driver_emp_no}번 승무원 정보를 찾을 수 없습니다.", flush=True)
            continue
        iframe_element = driver.find_element(By.ID, "frmReport")
        driver.switch_to.frame(iframe_element)

        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "html")))
        except TimeoutException:
            print(f"Timeout:: iframe 정보를 찾을 수 없습니다.")
            continue
            
        inner_html_element = driver.find_element(By.TAG_NAME, "html")
        inner_body_element = driver.find_element(By.TAG_NAME, "body")
        pop_diag_div = driver.find_element(By.ID, "pop-diagnosis")
        content_div = driver.find_element(By.ID, "content-01")
        top_btn = driver.find_element(By.CLASS_NAME, "page-btn").find_element(By.XPATH, "//a[@class='print' and @onclick='do_report()']")
        top_btn.click()

        WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 2)
        driver.switch_to.window(driver.window_handles[2])
        time.sleep(1)

        driver.find_element(By.ID, "targetDiv1")
        driver.find_element(By.TAG_NAME, "div")
        driver.find_element(By.CLASS_NAME, "report_menu_div")
        driver.find_element(By.TAG_NAME, "tr")
        driver.find_element(By.CLASS_NAME, "report_menu_table_td")
        driver.find_element(By.CLASS_NAME, "report_menu_table_td_div")
        driver.find_element(By.TAG_NAME, "nobr")
        report_top_btns = driver.find_elements(By.CLASS_NAME, "report_menu_button")

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
                        break
                break
            
def get_dangerous_driver_report_list (conn, login_id: str, password: str, year_month: str, company_id: int):
    driver = login(login_id, password)

    dangerous_driver_list = get_dangerous_driver_list(conn, year_month=year_month, company_id=company_id)
    dangerous_driver_emp_no_list = dangerous_driver_list["emp_no"].to_numpy()
    
    download_pdf_files(driver, dangerous_driver_emp_no_list)
    input("if press enter, i quit")
    driver.quit()
    
