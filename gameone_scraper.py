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

# 1. 크롬 브라우저 실행
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# 2. 게임원 로그인
driver.get("https://www.gameone.kr/member/login")
wait = WebDriverWait(driver, 10)

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

# 3. 2026시즌 타자 기록 페이지 접속
target_url = "https://www.gameone.kr/club/info/ranking/hitter?club_idx=14380&season=2026&kind=5"
driver.get(target_url)

print("페이지 로딩 및 데이터 불러오는 중...")
time.sleep(2)

# ★ 수정된 부분 1: '규정타석 미달' 표가 화면에 나타나도록 페이지 맨 아래로 스크롤
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(2) # 스크롤 후 미달 데이터가 뜰 때까지 대기

# 4. 데이터 추출 및 중복 제거 병합
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

try:
    tables = pd.read_html(StringIO(str(soup)))
    
    # 빈 표를 제외하고 데이터가 있는 표만 리스트에 담기
    valid_tables = [tbl for tbl in tables if len(tbl) > 0]
    
    if len(valid_tables) > 0:
        # 찾아낸 모든 표를 위아래로 합치기
        df_combined = pd.concat(valid_tables, ignore_index=True)
        
        # ★ 수정된 부분 2: '틀 고정' 때문에 숨겨져 있던 완전히 똑같은 중복 행 제거
        df_combined = df_combined.drop_duplicates()
        
        # CSV 파일로 저장
        df_combined.to_csv("gameone_hitter_2026.csv", index=False, encoding="utf-8-sig")
        print("성공! 중복 데이터가 제거된 전체 기록이 하나의 파일(gameone_hitter_2026.csv)로 저장되었습니다.")
        
    else:
        print("데이터 추출 실패: 해당 페이지에서 기록 표(Table)를 찾지 못했습니다.")
        
except Exception as e:
    print(f"데이터 변환 중 에러 발생: {e}")

driver.quit()