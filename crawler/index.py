from selenium import webdriver
import os
import platform

def get_default_download_path():
    if platform.system() == "Windows":
        return os.path.join(os.environ["USERPROFILE"], "Downloads")
    elif platform.system() == "Darwin":  # macOS
        return os.path.join(os.path.expanduser("~"), "Downloads")
    else:  # Linux
        return os.path.join(os.path.expanduser("~"), "Downloads")

def load_web_driver(user_data_dir: str = None):
    chrome_options = webdriver.ChromeOptions()

    # if(user_data_dir is not None):
    #     chrome_options.add_argument(f"user-data-dir={user_data_dir}")  # 사용자 데이터 저장 경로
    # else:
    #     chrome_options.add_argument(f"user-data-dir='/usr/src/chrome'")  # 사용자 데이터 저장 경로
    chrome_options.binary_location = '/usr/src/chrome'  # Chromium 경로
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    return driver