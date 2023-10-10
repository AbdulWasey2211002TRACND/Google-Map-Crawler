from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import os
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.common.keys import Keys
import pandas as pd
import requests_html
import re
import csv
from selenium.webdriver.support.ui import WebDriverWait


class GoogleMaps:
    def __init__(self):
        options = webdriver.ChromeOptions()
        print("Crawler Logs: Starting the crawler....")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument("--headless=new")
        self.driver = webdriver.Chrome(options=options)
        self.actionChains = ActionChains(self.driver)
        self.wait = WebDriverWait(self.driver, 20)
        self.driver.get("https://www.google.com/maps")
        self.file_path = "Scrapper Keywords.xlsx"
        self.usa_states =  [
            "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado",
            "Connecticut", "Delaware", "Florida", "Georgia", "Hawaii", "Idaho",
            "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana",
            "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota",
            "Mississippi", "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire",
            "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota",
            "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina",
            "South Dakota", "Tennessee", "Texas", "Utah", "Vermont", "Virginia", "Washington",
            "West Virginia", "Wisconsin", "Wyoming"
        ]
        self.template = " Companies in "

    def load_keywords(self):
        try:
            df = pd.read_excel(self.file_path)
            return df["Company Name"].to_list()
        except:
            return "Crawler Error: Somwthing went wrong in Loading Keywords"

    def save_csv_file(self, scrapped_data, keyword):
        try:
            print(f"Crawler Logs: Saving Scrapped Data for keyword:{keyword}")
            folder_path = "Google Map Results"
            csv_file = os.path.join(folder_path, f"{keyword}.csv")
            fieldnames = ["Name", "Phone", "Location","Company_Url"]

            with open(csv_file, mode='w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                for data in scrapped_data:
                    writer.writerow(data)
        except Exception as e:
            print(
                f"Crawler Error: Something went wrong in file creation. Error: ", str(e))

        print(f"Crawler Logs: CSV file '{csv_file}' has been created.")

    def google_map_crawler(self):
        try:
            time.sleep(5)
            keywords = self.load_keywords()
            for keyword in keywords:
                for state in self.usa_states:
                    complete_keyword = keyword+self.template+state+ ', Usa'
                    print(
                        f"Crawler Logs: Crawling Google Maps for keyword: {complete_keyword}.")
                    try:
                        self.driver.find_element(
                            By.XPATH, '//*[@id="searchboxinput"]').clear()
                    except:
                        pass

                    try:
                        self.driver.find_element(
                            By.XPATH, '//*[@id="searchboxinput"]').send_keys(complete_keyword)
                        self.driver.find_element(
                            By.XPATH, '//*[@id="searchbox-searchbutton"]').click()
                        time.sleep(5)

                        results = self.driver.find_elements(
                            By.XPATH, "//a[@class='hfpxzc']")
                        break_condition = False
                        focus_element = self.driver.find_element(
                            By.ID, 'zero-input')
                        while not break_condition:
                            temp = results[-1]
                            self.actionChains.scroll_to_element(
                                results[-1]).perform()
                            self.actionChains.move_to_element(
                                focus_element).click().perform()
                            for i in range(3):
                                self.actionChains.send_keys(
                                    Keys.ARROW_DOWN).perform()
                                time.sleep(2)
                            self.wait_for_element_location_to_be_stable(temp)

                            results = self.wait.until(EC.presence_of_all_elements_located(
                                (By.XPATH, "//a[@class='hfpxzc']")))
                            if results[-1] == temp:
                                break_condition = True
                        self.driver.save_screenshot(f"Screenshots\{complete_keyword}.png")
                        self.google_map_scrapper(self.driver.page_source, complete_keyword)

                    except Exception as e:
                        print(f"Crawler Error: ", str(e))
                        pass

        finally:
            print("Crawler Logs: Srapping finished. Crawler is Stopping.")
            self.driver.quit()

    def google_map_scrapper(self, html, keyword):
        print(f"Crawler Logs: Scrapping Google Maps for keyword: {keyword}.")
        soup = BeautifulSoup(html, "lxml")
        results = soup.find_all('a', 'hfpxzc')
        result = []
        for i in results: 
            try:
                inner_link = i.get('href')
                name,phone,location = self.google_map_inner_link_scrap(inner_link)
                data = {
                    "Name": name,
                    "Phone": phone,
                    "Location": location,
                    "Company_Url":inner_link
                }
                result.append(data)
            except Exception as e:
                print(f"Crawler Error: Something went wrong. Error: ", str(e))
                pass

        self.save_csv_file(result, keyword)
        return soup

    def google_map_inner_link_scrap(self, url):
        session = requests_html.HTMLSession()
        response = session.get(url)
        response.html.render()
        inner_link_html = BeautifulSoup(response.html.html, "lxml")
        name = inner_link_html.find('h1', 'DUwDvf lfPIob').text
        print(f"Crawler Logs: Company: {name} scrapped successfully.")

        location = inner_link_html.find(
            'div', 'Io6YTe fontBodyMedium kR99db').text
        location = self.extract_zip_code(location)
    
        try:
            phone = inner_link_html.find_all(
                'div', 'Io6YTe fontBodyMedium kR99db')[2].text
            
            check_percentage = self.calculate_percentage_of_numbers(phone)
            if check_percentage<20:
                phone = inner_link_html.find_all(
            'div', 'Io6YTe fontBodyMedium kR99db')[3].text
                
            check_percentage = self.calculate_percentage_of_numbers(phone)
            if check_percentage<20:
                phone = inner_link_html.find_all(
            'div', 'Io6YTe fontBodyMedium kR99db')[4].text
                
            check_percentage = self.calculate_percentage_of_numbers(phone)
            if check_percentage<20:
                phone = "Not Available"
                
        except:
            phone = "Not Available"

        return name,phone,location

    def wait_for_element_location_to_be_stable(self, element):
        initial_location = element.location
        previous_location = initial_location
        start_time = time.time()
        while time.time() - start_time < 1:
            current_location = element.location
            if current_location != previous_location:
                previous_location = current_location
                start_time = time.time()
            time.sleep(1)

    def calculate_percentage_of_numbers(self,phone):
        total_characters = len(phone)
        digit_count = sum(1 for char in phone if char.isdigit())
        percentage = (digit_count / total_characters) * 100
        return percentage

    def extract_zip_code(self,address):
        zip_code_pattern = r'\b\d{5}(?:-\d{4})?\b'
        matches = re.findall(zip_code_pattern, address)
        if matches:
            try:
                zip_code = matches[0]
                return zip_code
            except:
                return address
        else:
            return address

try:
    crawler = GoogleMaps()
    crawler.google_map_crawler()
except:
    print("Crawler Error: Somwthing went wrong")