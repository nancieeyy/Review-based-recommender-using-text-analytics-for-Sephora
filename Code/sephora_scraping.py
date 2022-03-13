#!/usr/bin/env python
# coding: utf-8

# In[3]:


get_ipython().system(' pip install selenium')

# In[9]:


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import time
import re
import math
import numpy as np

# Replace with the local location of chromedriver.exe Path
driver_path = '/Users/jainn/Course/INSY669/groupproject/chromedriver'


def get_product_reviews(url, driver_path):
    print(url)
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_argument("disable-infobars")
    options.add_argument("--disable-extensions")
    driver = webdriver.Chrome(driver_path)
    review = []
    use_old_format = False
    try:

        # driver.get("https://www.sephora.com/product/crybaby-coconut-oil-shine-serum-P439093?skuId=2122083&icid2=just%20arrived:p439093")
        # driver.get("https://www.sephora.com/ca/en/product/lip-sleeping-mask-P420652?skuId=1966258&icid2=products%20grid:p420652:product")
        driver.get(url)
        elem = driver.find_element(By.TAG_NAME, "body")
        no_of_pagedowns = 20
        while no_of_pagedowns:
            elem.send_keys(Keys.PAGE_DOWN)
            time.sleep(0.2)
            no_of_pagedowns -= 1
        number_reviews = 0
        WebDriverWait(driver, 5)
        review_section = driver.find_element(By.ID, "ratings-reviews-container")
        try:
            number_reviews = \
            review_section.find_element(By.XPATH, "./div[2]/div[6]").find_element(By.XPATH, './*').get_attribute(
                'innerHTML').split("of")[1].split()[0].strip().lower()
            if 'k' in number_reviews:
                number_reviews = int(number_reviews.replace('k', ''))
                number_reviews = number_reviews * 1000
        except NoSuchElementException:
            WebDriverWait(review_section, 10).until(EC.presence_of_element_located((By.XPATH, "./div[2]/div[4]")))
            number_reviews = \
            review_section.find_element(By.XPATH, "./div[2]/div[4]").find_element(By.XPATH, './*').get_attribute(
                'innerHTML').split("of")[1].split()[0].strip().lower()
            if 'k' in number_reviews:
                number_reviews = int(number_reviews.replace('k', ''))
                number_reviews = number_reviews * 1000
            use_old_format = True

        number_reviews = int(number_reviews)
        if (number_reviews > 6):
            sort_button = review_section.find_element(By.CSS_SELECTOR, "button[aria-label='Sort']")
            sort_button.click()
            newest_button = review_section.find_element(By.XPATH, "./div[2]/ul/li[last()]/button")
            newest_button.click()
            WebDriverWait(driver, 5)

        required_review_pages = 3
        # page_button = review_section.find_elements(By.XPATH, "//*[@data-at='pagination_page']")

        for index in range(min(math.ceil(float(number_reviews / 6)), required_review_pages)):
            review_section = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "ratings-reviews-container")))

            if use_old_format:
                rev = review_section.find_element(By.XPATH, "./div[2]/div[4]")
            else:
                rev = review_section.find_element(By.XPATH, "./div[2]/div[6]")

            WebDriverWait(rev, 10).until(EC.presence_of_element_located((By.XPATH, "./div")))
            rev_el = rev.find_elements(By.XPATH, "./div")

            for i, rev_element in enumerate(rev_el):
                if i == 0 or i % 2 == 1:
                    continue
                else:
                    time.sleep(5)
                    review_next = WebDriverWait(rev_el[i], 10).until(
                        EC.presence_of_element_located((By.XPATH, "./div/div[2]/div")))
                    review.append(review_next.get_attribute('innerHTML'))
            if math.ceil(float(number_reviews / 6)) // 6 <= index + 1:
                break
            else:
                review_section.find_element(By.XPATH, "./div[2]/ul/li[last()]/button").click()
            time.sleep(2)
        driver.quit()
    except NoSuchElementException as nse:
        if not len(review) > 0:
            review = None
            # raise nse
    except Exception as e:
        #print(e)
        if not len(review) > 0:
            review = None
        # raise e
    finally:
        driver.quit()
    return review


def get_items_from_product_page(main_url, driver_path):
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_argument("disable-infobars")
    options.add_argument("--disable-extensions")
    driver = webdriver.Chrome(driver_path)
    driver.get(main_url)
    elem = driver.find_element(By.TAG_NAME, "body")
    no_of_pagedowns = 20
    while no_of_pagedowns:
        elem.send_keys(Keys.PAGE_DOWN)
        time.sleep(0.2)
        no_of_pagedowns -= 1
    prod_grid = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div/div/div/div/div[2]/main/div")
    while True:
        # print("loading....")
        try:
            button = prod_grid.find_elements(By.XPATH, "./div")[1].find_element(By.XPATH, "./div[last()]/button")
            if button.get_attribute("innerHTML") == 'Show More Products':
                button.click()
                time.sleep(0.5)
            else:
                flag = False
        except NoSuchElementException:
            break
    prod_grid = driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div/div/div/div/div[2]/main/div")
    items_div = prod_grid.find_elements(By.XPATH, "./div[2]/div")
    prod_name = []
    brand = []
    price = []
    rating = []
    url = []
    review_count = []
    for i in range(8, len(items_div) - 1):
        try:
            price.append(items_div[i].find_element(By.TAG_NAME, 'b').find_element(By.TAG_NAME, 'span').get_attribute(
                'innerHTML'))
            brand.append(items_div[i].find_element(By.TAG_NAME, 'span').get_attribute('innerHTML'))
            prod_name.append(items_div[i].find_element(By.CLASS_NAME, 'ProductTile-name').get_attribute('innerHTML'))
            rating.append(items_div[i].find_element(By.XPATH, "./a/div[2]/span").get_attribute("aria-label"))
            review_count.append(
                items_div[i].find_element(By.XPATH, "./a/div[2]/span[last()]").get_attribute("innerHTML"))
            url.append(items_div[i].find_element(By.XPATH, "./a").get_attribute("href"))
        except NoSuchElementException:
            continue
    items_dict = {'prod_name': prod_name, 'brand': brand, 'price': price, 'rating': rating,
                  'review_count': review_count, 'url': url}
    df = pd.DataFrame(items_dict)
    driver.quit()
    return df


main_url = 'https://www.sephora.com/ca/en/shop/moisturizing-cream-oils-mists?ref=filters[Ingredient%20Preferences]=Vegan'
items = get_items_from_product_page(main_url, driver_path)
items['reviews'] = items['url'].apply(lambda x: get_product_reviews(x, driver_path))
#items.to_csv('sephora_items.csv')

eye_cream_url='https://www.sephora.com/ca/en/shop/eye-cream-dark-circles?ref=filters[Ingredient%20Preferences]=Vegan'
eye_cream_items=get_items_from_product_page(eye_cream_url,driver_path)
eye_cream_items['reviews']=eye_cream_items['url'].apply(lambda x: get_product_reviews(x,driver_path))

merged_df = pd.concat([eye_cream_items, items])
merged_df.to_csv('sephora_items.csv')


