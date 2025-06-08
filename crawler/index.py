from selenium import webdriver

def load_web_driver(user_data_dir: str = None):
    chrome_options = webdriver.ChromeOptions()
    if(user_data_dir is not None):
        chrome_options.add_argument(f"user-data-dir={user_data_dir}")  # 사용자 데이터 저장 경로
    # chrome_options.add_argument("--headless=new")

    driver = webdriver.Chrome(options=chrome_options)
    return driver