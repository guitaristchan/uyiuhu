import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from io import StringIO

# 중복 표 제거 함수
def get_unique_tables(tables):
    valid_tables = [t for t in tables if len(t) > 0]
    unique_tables = []
    for t in valid_tables:
        if not any(t.equals(ut) for ut in unique_tables):
            unique_tables.append(t)
    return unique_tables

# 1. 크롬 브라우저 실행 및 로그인
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 10)

driver.get("https://www.gameone.kr/member/login")

try:
    id_input = wait.until(EC.presence_of_element_located((By.ID, "user_id")))
    id_input.send_keys("guitarchan")
    
    pw_input = driver.find_element(By.ID, "passwd")
    pw_input.send_keys("Chan0827!@") # ★ 실제 비밀번호로 변경하세요
    pw_input.send_keys(Keys.ENTER)
    
    print("로그인 처리 중...")
    time.sleep(2)
except Exception as e:
    print(f"로그인 중 문제 발생: {e}")

# 2. 타자 기록 수집
print("타자 기록 페이지 로딩 중...")
driver.get("https://www.gameone.kr/club/info/ranking/hitter?club_idx=14380&season=2026&kind=5")
time.sleep(2)
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(2)

soup_h = BeautifulSoup(driver.page_source, 'html.parser')
tables_h = pd.read_html(StringIO(str(soup_h)))
unique_h_tables = get_unique_tables(tables_h)


# 3. 투수 기록 수집
print("투수 기록 페이지 로딩 중...")
driver.get("https://www.gameone.kr/club/info/ranking/pitcher?club_idx=14380")
time.sleep(2)
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(2)

soup_p = BeautifulSoup(driver.page_source, 'html.parser')
tables_p = pd.read_html(StringIO(str(soup_p)))
unique_p_tables = get_unique_tables(tables_p)


# 4. 하나의 CSV 파일에 제목과 함께 통합 저장
file_name = "gameone_records_2026_combined.csv"

try:
    with open(file_name, "w", encoding="utf-8-sig") as f:
        
        # [타자 정규 기록]
        if len(unique_h_tables) > 0:
            df_h_main = unique_h_tables[0].rename(columns={"경기수": "게임수", "경기": "게임수"})
            f.write("=== 타자 기록 (정규) ===\n")
            df_h_main.to_csv(f, index=False)
            
        # [타자 미달 기록]
        if len(unique_h_tables) > 1:
            df_h_under = unique_h_tables[1].rename(columns={"경기수": "게임수", "경기": "게임수"})
            f.write("\n=== 타자 기록 (규정타석 미달) ===\n")
            df_h_under.to_csv(f, index=False)
            
        # [투수 정규 기록]
        if len(unique_p_tables) > 0:
            df_p_main = unique_p_tables[0].rename(columns={"경기수": "게임수", "경기": "게임수"})
            f.write("\n=== 투수 기록 (정규) ===\n")
            df_p_main.to_csv(f, index=False)
            
        # [투수 미달 기록]
        if len(unique_p_tables) > 1:
            df_p_under = unique_p_tables[1].rename(columns={"경기수": "게임수", "경기": "게임수"})
            f.write("\n=== 투수 기록 (규정이닝 미달) ===\n")
            df_p_under.to_csv(f, index=False)

    print(f"성공! 모든 기록이 {file_name} 파일 하나에 제목별로 나뉘어 저장되었고, '게임수'로 열 이름이 완벽하게 통일되었습니다.")

except Exception as e:
    print(f"CSV 저장 중 에러 발생: {e}")

driver.quit()