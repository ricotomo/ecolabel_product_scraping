from ast import Pass
from msilib.schema import Error
from lxml import html
import time
import logging
import os
import requests
from selenium import webdriver


from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


import pandas as pd

#path to files
file_path="C:/Users/morit/Documents/School/MSc - Fintech Thesis/Code"

#setup the logger
logging.basicConfig(filename=file_path+"log.txt", level=logging.DEBUG)

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
        driver.get("https://www.svanen.se/en/categories/electronics/")
    elif label == "BA":
        driver.get("https://www.blauer-engel.de/en/products")
        driver.implicitly_wait(10)
        #get rid of cookies overlay
        try:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"]'))).click()
        except:
            logging.warning("Exception while trying to close the cookies dialogue")
    else:
        #print("entered else in getWebsite")
        return Error
    return "Success"

#get the categories of electronics

def getCategories(label=label):
    categories_list = []
    if label == "NS":
        categories = driver.find_elements_by_class_name("category")
    elif label =="BA":
        #get rid of cookies overlay
        try:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH,'//*[@id="CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"]'))).click()
        except:
            print("ERROR: Exception while trying to close the cookies dialogue")
        driver.find_elements_by_xpath("//*[text()='Product categories']")[0].click()
        driver.find_elements_by_xpath("//*[text()='Green-IT / Household Appliances']")[0].click()
        categories = driver.find_elements_by_class_name("m-bep_categories__childlink")
    else:
        return None    
    for category in categories:
        #Blue angel returns some empty category strings so we make sure not to save these here
        if category.text != '':
            categories_list.append(category.text)
    return categories_list 

def getCategoryPages(categories, label=label):
    category_pages_list = []
    if label == "NS" or "BA":
        for category in categories:
                elements = driver.find_elements_by_link_text(category)
                for element in elements:
                    category_pages_list.append([category, element.get_attribute('href')])
    # elif label == "BA":
    #     Pass
    return category_pages_list

def getProductPages(categoryPages, label=label):
    product_pages_list=[]
    for page in categoryPages:
        driver.get(page[1])
        if label == "NS":
            elements = driver.find_elements_by_xpath("//a[@class='d-flex flex-column flex-wrap align-items-center-x col-8 col-lg-9 px-3']")
            #print(elements)
        elif label == "BA":
            elements = driver.find_elements_by_xpath("//a[@class='m-bep_raluz__productslink']")
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
        if label == "BA":
            name = driver.find_element_by_xpath("//h1[@class='m-bep_productdetail__title']").text
            category = page[0]
            product_details_list.append([category, name])

    return product_details_list


##Nordic Swan
# label="NS"
# getWebsite(label)
# NS_Categories=getCategories(label)
# #print(NS_Categories)
# NS_Category_Pages = getCategoryPages(NS_Categories, label)
# #print(NS_Category_Pages)
# NS_Product_Pages=getProductPages(NS_Category_Pages, label)
# #print(NS_Product_Pages)
# NS_Product_Details=getProductDetails(NS_Product_Pages, label)
# #print(NS_Product_Details)

# ##Write Nordic Swan products to csv file
# df = pd.DataFrame(NS_Product_Details)
# df.columns = ['Category', 'Product']
# df['Label'] = "Nordic Swan"
# # print(df.head(5))
# # print(os.getcwd())

# df.to_csv(file_path+"/product_database.csv", index=False, encoding="utf-8")

##Blue Angel
label ="BA"
getWebsite(label)
BA_Categories=getCategories(label)
print(BA_Categories)
BA_Category_Pages = getCategoryPages(BA_Categories, label)
print(BA_Category_Pages)
BA_Product_Pages=getProductPages(BA_Category_Pages, label)
print(BA_Product_Pages)
BA_Product_Details=getProductDetails(BA_Product_Pages[0:2], label)
print(BA_Product_Details)


#set timer to 3 seconds in case there is a  delay in loading
#time.sleep (3)


driver.close()