from requests.packages.urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import csv
import os
import requests
from urllib.parse import unquote

content = 'original-links.csv'


def test_headless_browser(driver):
    driver.get("https://www.baidu.com")
    assert "百度" in driver.title
    print("Headless Firefox is working correctly.")


def download_pdf(url, filename):
    with requests.Session() as session:
        retries = Retry(total=5, backoff_factor=0.1,
                        status_forcelist=[500, 502, 503, 504])
        session.mount('https://', HTTPAdapter(max_retries=retries))
        try:
            response = session.get(url)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print("HTTP error occurred: " + str(err))
        except Exception as err:
            print("An error occurred: " + str(err))
        else:
            with open(filename, 'wb') as file:
                file.write(response.content)


def find_target(driver, url):
    try:
        driver.get(url)
        driver.implicitly_wait(10)
        # Tries to find the first iframe element
        iframe = driver.find_element(By.TAG_NAME, 'iframe')
    except Exception as e:
        print(f"An error occurred while trying to find the iframe: {e}")
        return None
    else:
        if iframe is not None:
            # Gets the 'src' attribute of the iframe
            src = iframe.get_attribute('src')
            # Replaces the unwanted part
            src = src.replace("/system/resource/pdfjs/viewer.html?file=", "")

            src = unquote(src)
            print(src)
            return src
        else:
            print("No iframe found.")
            return None


# Set up the webdriver
options = Options()
options.add_argument("--headless")  # Run in headless mode
driver = webdriver.Firefox(options=options)
test_headless_browser(driver)

with open(content, 'r', encoding='utf-8') as file:
    reader = csv.reader(file)
    next(reader)  # Skip the header
    for row in reader:
        url, name, academy = row
        directory = os.path.join('.', academy)  # Create the directory path
        if not os.path.exists(directory):  # If the directory does not exist
            os.makedirs(directory)  # Create the directory
        # Create the filename
        filename = os.path.join(directory, name + '.pdf')
        print(filename, url)
        realurl = find_target(driver, url)
        if (realurl is not None):
            download_pdf(realurl, filename)
        else:
            print(filename, "not found")
            # Open the text file in append mode ('a') and write the filename to it
            with open('not_found.txt', 'a', encoding='utf-8') as f:
                f.write(filename + '\n')


driver.quit()  # Close the browser
