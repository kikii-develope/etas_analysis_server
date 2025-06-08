from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def check_jsessionid(driver):
    """
    JSESSIONID 쿠키의 존재 여부를 확인합니다.
    
    Args:
        driver: Selenium WebDriver 인스턴스
        
    Returns:
        tuple: (bool, str) - (JSESSIONID 존재 여부, JSESSIONID 값 또는 None)
    """
    try:
        cookies = driver.get_cookies()
        for cookie in cookies:
            if cookie['name'] == 'JSESSIONID':
                return True
        driver.quit()
        return False
    except Exception as e:
        print(e)
        return False

def check_main_page(driver, main_page_url):
    """
    메인 페이지에 접근 가능한지 확인합니다.
    
    Args:
        driver: Selenium WebDriver 인스턴스
        main_page_url: 확인할 메인 페이지 URL
        
    Returns:
        bool: 메인 페이지 접근 가능 여부
    """
    try:
        # 현재 URL이 메인 페이지가 아니라면 이동
        if driver.current_url != main_page_url:
            driver.get(main_page_url)
            
        # 페이지 로딩 대기
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # 로그인 상태 확인 (로그아웃 버튼 존재 여부)
        try:
            header_div = driver.find_element(By.ID, "header")
            return "로그아웃" in header_div.get_attribute("outerHTML")
        except NoSuchElementException:
            return False
            
    except (TimeoutException, NoSuchElementException):
        return False 