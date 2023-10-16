from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import os
import csv
from apify_client import ApifyClient
import time
import pandas as pd


class Facebook:
    def __init__(self):
        options = webdriver.ChromeOptions()
        print("Crawler Logs: Starting the crawler....")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_argument("--window-size=1920,1080")
        options.add_argument('--disable-notifications')
        self.email = "waseysiddique11@gmail.com"
        self.password = "wf1234"
        self.facebook_pages_url = "https://www.facebook.com/search/pages?q="
     #   options.add_argument("--headless=new")
        self.driver = webdriver.Chrome(options=options)
        self.driver.get("https://www.facebook.com/")
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
        self.template = " Companies in: "

    def load_keywords(self):
        try:
            df = pd.read_excel(self.file_path)
            return df["Company Name"].to_list()
        except:
            return "Crawler Error: Somwthing went wrong in Loading Keywords"

    def save_csv_file(self, scrapped_data, keyword):
        try:
            print(f"Crawler Logs: Saving Scrapped Data for keyword:{keyword}")
            folder_path = "Facebook Results"
            csv_file = os.path.join(folder_path, f"{keyword}.csv")
            fieldnames = ["Name", "Phone","Company_Url"]

            if os.path.exists(csv_file):
                mode = 'a' 
            else:
                mode = 'w'  

            with open(csv_file, mode=mode, newline='',encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)

                if mode == 'w':
                    writer.writeheader()

                for data in scrapped_data:
                    writer.writerow(data)

        except Exception as e:
            print(
                f"Crawler Error: Something went wrong in file creation. Error: ", str(e))

        print(f"Crawler Logs: CSV file '{csv_file}' has been created.")

    def facebook_crawler(self):
        try:
            keywords = self.load_keywords()
            time.sleep(2)
            self.driver.find_element(By.XPATH, '//*[@id="email"]').send_keys(self.email)
            time.sleep(1)
            self.driver.find_element(By.XPATH, '//*[@id="pass"]').send_keys(self.password)
            time.sleep(1)
            self.driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div[1]/div/div/div/div[2]/div/div[1]/form/div[2]/button').click()
            time.sleep(15)
            for keyword in keywords:
                for state in self.usa_states:
                    complete_keyword = keyword+self.template+state+ ', Usa'
                    self.driver.get(self.facebook_pages_url+complete_keyword)
                    time.sleep(5)

                    try: 
                        for i in range(20):
                            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                            time.sleep(1)

                    except:
                        pass

                    urls = self.facebook_scrapper(self.driver.page_source,keyword)
                    results = []
                    for url in urls:
                        self.driver.get(url)
                        time.sleep(3)
                        results.append(self.facebook_inner_link_scrap(self.driver.page_source,url))
                    self.save_csv_file(results,"Results")




        except Exception as e:
            print(f"Crawler Error: ", str(e))
            pass

        finally:
            print("Crawler Logs: Srapping finished. Crawler is Stopping.")
            self.driver.quit()

    def facebook_scrapper(self, html, keyword):
        print(f"Crawler Logs: Scrapping Google Maps for keyword: {keyword}.")
        soup = BeautifulSoup(html, "lxml")
        results = soup.find_all('a', 'x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz xt0b8zv xzsf02u x1s688f')
        all_urls = []
        for i in results: 
            try:
                inner_link = i.get('href')
                all_urls.append(inner_link)
            except Exception as e:
                print(f"Crawler Error: Something went wrong. Error: ", str(e))
                pass
        
  
        return all_urls

    def facebook_inner_link_scrap(self, html,url):
        soup = BeautifulSoup(html, "lxml")

        scrapped_results = []

        Name = soup.find('div','x1e56ztr x1xmf6yo').text
       
        try:
            Phone =  soup.find_all('div','x9f619 x1n2onr6 x1ja2u2z x78zum5 x2lah0s x1nhvcw1 x1qjc9v5 xozqiw3 x1q0g3np xyamay9 xykv574 xbmpl8g x4cne27 xifccgj')[0].text
        except:
            Phone = 'Not Available'
        
        Company_Url  = url
       
        data = {
            "Name":Name,
            "Phone": Phone,
            "Company_Url": Company_Url
        }

        scrapped_results.append(data)
            
        return scrapped_results

        


c = Facebook()
c.facebook_crawler()

