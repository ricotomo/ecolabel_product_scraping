from lxml import html
import time
import os
import requests
from selenium import webdriver


from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import pandas as pd

##Firefox
# from webdriver_manager.firefox import GeckoDriverManager
# driver = webdriver.Firefox(GeckoDriverManager().install())

# headless option to avoid opening a new browser window
options = Options()
options.add_argument('--headless')

##Chrome
from webdriver_manager.chrome import ChromeDriverManager
driver = webdriver.Chrome(ChromeDriverManager().install())
#driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)



#set label
label=None

##Generic functions

#get webpage of the label
def getWebsite(label=label):
    if label == "NS":
        driver=driver.get("https://www.svanen.se/en/categories/electronics/")
    elif label == "BA":
        driver=driver.get("https://www.blauer-engel.de/en/products")
    else:
        driver=None
    return driver

#get the categories of electronics

def getCategories(driver=driver, label=label):
    categories_list = []
    if label == "NS":
        #categories = driver.find_element(By.CLASS_NAME, "category-name")
        categories = driver.find_elements_by_class_name("category")
        #driver.findElement(By.LocatorStrategy("LocatorValue"))
    elif label =="BA":
        driver.find_elements_by_xpath("//*[text()='Product categories']").click()
        categories = driver.find_elements_by_class_name("m-bep_categories__listitemtext")
    else:
        return None    
    for category in categories:
        categories_list.append(category.text)
    return categories_list 

def getCategoryPages(categories, driver=driver, label=label):
    category_pages_list = []
    if label == "NS":
        for category in categories:
                elements = driver.find_elements_by_link_text(category)
                for element in elements:
                    category_pages_list.append([category, element.get_attribute('href')])
    return category_pages_list

def getProductPages(categoryPages, driver=driver, label=label):
    product_pages_list=[]
    for page in categoryPages:
        driver.get(page[1])
        if label == "NS":
            elements = driver.find_elements_by_xpath("//a[@class='d-flex flex-column flex-wrap align-items-center-x col-8 col-lg-9 px-3']")
            #print(elements)
        else:
            elements = None
        for element in elements:
                product_pages_list.append([page[0],element.get_attribute('href')])
    return product_pages_list

def getProductDetails(productPages, label=label):
    product_details_list=[]
    for page in productPages:
        driver.get(page[1])
        if label == "NS":
            name = driver.find_element_by_xpath("//h1[@class='d-flex justify-content-between mt-7']").text
            category = page[0]
            product_details_list.append([category, name])

    return product_details_list


##Nordic Swan
# label="NS"
# driver=getWebsite(label)
# NS_Categories=getCategories(driver,label)
# #print(NS_Categories)
# NS_Category_Pages = getCategoryPages(NS_Categories, driver, label)
# #print(NS_Category_Pages)
# NS_Product_Pages=getProductPages(NS_Category_Pages, driver, label)
# #print(NS_Product_Pages)
# NS_Product_Details=getProductDetails(NS_Product_Pages, label)
# #print(NS_Product_Details)

# df = pd.DataFrame(NS_Product_Details)
# df.columns = ['Category', 'Product']
# df['Label'] = "Nordic Swan"
# # print(df.head(5))
# # print(os.getcwd())

#df.to_csv("C:/Users/morit/Documents/School/MSc - Fintech Thesis/Code/product_database.csv", index=False, encoding="utf-8")

##Blue Angel
label ="BA"
driver=getWebsite(label)
BA_Categories=getCategories(driver,label)
print(BA_Categories)


#set timer to 3 seconds in case there is a  delay in loading
#time.sleep (3)


driver.close()