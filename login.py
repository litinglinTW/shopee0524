import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def login_page():
    st.title("🔐 登入蝦皮帳號")
    username = st.text_input("請輸入蝦皮帳號")
    password = st.text_input("請輸入密碼", type="password")

    if st.button("登入"):
        with st.spinner("正在嘗試登入..."):
            try:
                CHROMEDRIVER_PATH = '/Users/yuchieh/Documents/蝦皮專案/chromedriver'

                service = Service(CHROMEDRIVER_PATH)
                options = webdriver.ChromeOptions()
                #options.add_argument("--headless")  # 不開啟瀏覽器畫面
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")

                driver = webdriver.Chrome(service=service, options=options)
                driver.get("https://seller.shopee.tw/")

                wait = WebDriverWait(driver, 10)
                wait.until(EC.presence_of_element_located((By.NAME, "loginKey"))).send_keys(username)
                driver.find_element(By.NAME, "password").send_keys(password)
                login_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "登入")]')))
                login_button.click()
                time.sleep(5)

                page_source = driver.page_source
                error_keywords = ["你的帳號或密碼不正確", "登入失敗，請稍後再試或使用其他登入方法"]

                if any(keyword in page_source for keyword in error_keywords):
                    st.error("❌ 登入失敗，請檢查帳號與密碼。")
                else:
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = username
                    st.session_state["password"] = password
                    st.session_state["driver"] = driver  # 關鍵！！
                    st.success("✅ 登入成功！")
            except Exception as e:
                st.error(f"🚨 發生錯誤：{e}")

if __name__ == "__main__":
    login_page()

