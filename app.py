from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import gspread

def is_element_present(driver, locator):
    try:
        driver.find_element(locator)
        return True
    except Exception:
        return False

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')  # Homepage with input form

@app.route('/scrape', methods=['POST'])
def scrape():
    location = request.form['location']
    industry = request.form['industry']

    try:

        chromedriver_path = r'C:\Users\Lenovo\Downloads\chromedriver-win64\chromedriver.exe'
        service = Service(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=service)

        url = f"https://www.google.com/maps/search/{industry}+{location}"
        driver.get(url)

        timeout = 100
        wait = WebDriverWait(driver, timeout)

        name = None
        address = None
        phone = None
        website = None

        if is_element_present(driver, By.CLASS_NAME, 'DUwDvf'):
            name = driver.find_element(By.CLASS_NAME, 'DUwDvf').text

        all_details = driver.find_elements(By.CLASS_NAME, 'CsEnBe')
        for detail in all_details:
            label = detail.get_attribute('aria-label')
            if label and 'address' in label.lower():
                address = label.split(':')[-1].strip()
            elif label and 'phone' in label.lower():
                phone = detail.get_attribute('innerText').replace(" ", "")
            elif label and 'website' in label.lower():
                website = detail.get_attribute('innerText').replace(" ", "")

        driver.quit()

        return render_template('results.html', name=name, address=address, phone=phone, website=website)

    except Exception as e:
        return render_template('error.html', error_message=str(e))

def store_data_in_sheet(name, address, phone, website):
    credentials_file = 'path/to/your/credentials.json'
    gc = gspread.service_account(filename=credentials_file)
    sheet=gc.open("gmaps").sheet1 
    data = [name, address, phone, website]
    sheet.append_row(data)

if __name__ == '__main__':
    app.run(debug=True)
