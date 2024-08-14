from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from io import BytesIO
import json
import os
import requests
from tqdm import tqdm
from urllib.parse import urljoin, urlparse
import urllib.request
import time
import concurrent.futures

class UrlScrapper():
    def __init__(self, url_template, max_images = 50, max_workers = 4):
        self.url_template = url_template
        self.max_images = max_images
        self.max_workers = max_workers
        #self.setup_enviroment()


    def setup_environment(self):
        os.environ["PATH"] += ":/usr/lib/chromium-browser/"
        os.environ["PATH"] += ":/usr/lib/chromium-browser/chromedriver"


    def get_url_images(self, term):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(options = options)

        url = self.url_template.format(search_term = term)
        driver.get(url)
        tags = driver.find_element(By.XPATH, '//*[@id="search-unified-content"]')

        pbar = tqdm(total = self.max_images, desc = f"Fetching images for {term}")
        
        # scroll window
        x = 0    
        while True:
            x += 1
            driver.execute_script("window.scrollBy(0, 500);")
            time.sleep(2)

            if x > 20:
                break  

        urls = []
        for i in range(1, self.max_images + 1):

            #img_tags = tags.find_elements(By.TAG_NAME, "img")
            src = tags.find_element(By.XPATH, '//div/div[1]/div[2]/div/div[2]/div[' + str(i) + ']/div/img').get_attribute("src")
            
            img_path = urljoin(url, src)
            img_path = img_path.replace("_m.jpg", "_b.jgp").replace("_n.jpg", "_b.jgp").replace("_w.jpg", "_b.jgp")

            if img_path == "https://combo.staticflickr.com/ap/build/images/getty/IStock_corporate_logo.svg":
                continue

            urls.append(img_path)
            pbar.update(1)
                
        pbar.close()
        driver.quit()
        return urls


    def scrape_urls(self, categories):
        """
        Call get_url_images method to get all urls of any object in categories

        Parameter:
        categories (dictionary): the dict of all object we need to collect image with format
        categories{"name_object": [value1, value2, ...]}

        Returns:
            all_urls (dictionary): Dictionary of urls of images
        """

        all_urls = {category: {} for category in categories}

        with concurrent.futures.ThreadPoolExecutor(max_workers = self.max_workers) as executor:
            future_to_term = {executor.submit(self.get_url_images, term): (category, term)
                              for category, terms in categories.items() for term in terms}
        
            for future in tqdm(concurrent.futures.as_completed(future_to_term), total = len(future_to_term),
                               desc = "Overall Progress"):
                category, term = future_to_term[future]
                
                try:
                    urls = future.result()
                    all_urls[category][term] = urls
                    print(f"\nNumber for images retrieved for {term}: {len(urls)}")
                
                except Exception as ex:
                    print(f"\n{term} generated an exception: {ex}")
        
        return all_urls
    
    
    def save_to_file(self, data, filename):
        """
        Save the data to JSON file

        Parameters:
        data (dict): The data to be saved
        filename (str): The name of the JSON file

        Return:
        None
        """

        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
        
        print(f"Data save to {filename}")