from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

driver = webdriver.Chrome()
driver.get("https://www.wikipedia.org")

search = driver.find_element(By.ID, "searchInput")
search.send_keys("Россия")
search.send_keys(Keys.ENTER)

wait = WebDriverWait(driver, 10)
heading = wait.until(expected_conditions.presence_of_element_located((By.ID, "firstHeading")))
assert "Россия" in heading.text

print("Тест прошёл успешно!")
driver.quit()