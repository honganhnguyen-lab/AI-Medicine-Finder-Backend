from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

opts = Options()
# comment next line to see the Chrome window
# opts.add_argument("--headless=new")
opts.add_argument("--window-size=1200,900")

service = Service()
d = webdriver.Chrome(options=opts, service=service)
d.get("https://www.google.com")
print("Title:", d.title)
d.quit()
