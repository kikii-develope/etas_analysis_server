from selenium import webdriver

def load_web_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument(f"user-data-dir=/Users/islee/Desktop/selenium-user-data")  # 사용자 데이터 저장 경로
    # chrome_options.add_argument("--headless=new")

    driver = webdriver.Chrome(options=chrome_options)
    return driver