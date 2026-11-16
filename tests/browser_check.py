"""End-to-end checks against the publicly deployed free Worker site."""
import csv
import os
import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

URL = "https://hatake-saisan-note.nakagawa01984.workers.dev/"
download_dir = Path(os.environ.get("RUNNER_TEMP", "/tmp")) / "hatake-browser-downloads"
download_dir.mkdir(parents=True, exist_ok=True)
opts = Options()
opts.add_argument("--headless=new")
opts.add_argument("--no-sandbox")
opts.add_argument("--disable-dev-shm-usage")
opts.add_argument("--window-size=1280,900")
opts.add_experimental_option("prefs", {
    "download.default_directory": str(download_dir),
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
})
driver = webdriver.Chrome(options=opts)
wait = WebDriverWait(driver, 25)
try:
    driver.execute_cdp_cmd("Page.setDownloadBehavior", {
        "behavior": "allow",
        "downloadPath": str(download_dir)
    })
    driver.get(URL)
    wait.until(lambda d: d.find_element(By.ID, "profit").text != "—")
    assert "畑の採算ノート" in driver.title
    assert driver.find_element(By.ID, "revenue").text == "85,000円"
    assert driver.find_element(By.ID, "cash").text == "26,500円"
    assert driver.find_element(By.ID, "profit").text == "-33,500円"

    rate = driver.find_element(By.ID, "saleRate")
    rate.clear()
    rate.send_keys("95")
    wait.until(lambda d: d.find_element(By.ID, "profit").text == "-24,500円")

    driver.find_element(By.ID, "save").click()
    assert "保存しました" in driver.find_element(By.ID, "status").text
    driver.refresh()
    wait.until(lambda d: d.find_element(By.ID, "profit").text == "-24,500円")
    assert driver.find_element(By.ID, "saleRate").get_attribute("value") == "95"

    driver.find_element(By.ID, "csv").click()
    csv_path = download_dir / "hatake-saisan.csv"
    for _ in range(30):
        if csv_path.exists() and csv_path.stat().st_size > 0:
            break
        time.sleep(1)
    assert csv_path.exists(), "CSV was not downloaded"
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.reader(f))
    assert ["項目", "値"] == rows[0]
    assert any(row[0] == "販売可能率（%）" and row[1] == "95" for row in rows)
    assert any(row[0] == "労働評価込み収支（円）" and row[1] == "-24500" for row in rows)

    driver.find_element(By.ID, "reset").click()
    wait.until(lambda d: d.find_element(By.ID, "profit").text == "-33,500円")

    print("PASS: live Chrome calculations, editing, local storage, CSV, reset")
finally:
    driver.quit()
