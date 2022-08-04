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
from selenium.webdriver.common.action_chains import ActionChains


import pandas as pd

import requests

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

#initialize label
label=None

##EPEAT special functions
## EPEAT offers a csv export function of the product catalogue. Because using this will be more robust than crawling all the data a script is setup to get and handle the exported file. 

def excelHandlerEPEAT(link):
    try:
        with requests.Session() as s:
            download = s.get(link)
            open("data.xlsx", "wb").write(download.content)
            df = pd.read_excel("data.xlsx", engine='openpyxl')
    except:
        logging.error("unable to download excel file from EPEAT")
        return None
    #products are listed by EPEAT for each country they are sold in. This leads to duplicate products. Drop these.
    df = df.drop_duplicates(subset='Product Name', keep="first")
    #the product list includes non-actively certified products. Drop these.
    df = df[df.Status == "Active"]
    #the product list also includes archived products. Drop these.
    df.drop(df.loc[df['Archived On']!="*"].index, inplace=True)
    #return only a list of product names
    df = df[['Product Name', 'Manufacturer']]
    return df

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
    elif label == "TCO":
        driver.get("https://tcocertified.com/product-finder/")
    elif label == "EPEAT":
        driver.get("https://epeat.net/")
    else:
        logging.error("The label name was not recognized or the website couldnt be retrieved via the getWebsite method")
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
    elif label == "TCO":
        categories = driver.find_elements_by_xpath("//div[@class='col-4 col-md-3 mb-4 mb-md-0 p-md-4 category text-uppercase text-center']/a")
    elif label == "EPEAT":
        categories = driver.find_elements_by_xpath("//div[@id='search-tabs']/ul/li/a/span")
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
        elif label == "TCO":
            product_table = driver.find_element_by_css_selector('table')
            elements=[]
            #PLACEHOLDER get pages and iterate over them
            for row in product_table.find_elements_by_css_selector('tr'):
                #scroll to row in table
                actions = ActionChains(driver)
                actions.move_to_element(row).perform()
                try:
                    row.click()
                    print(driver.current_url)
                    elements.append(driver.current_url)
                    #close the product overlay so we can look for the next one
                    driver.find_element_by_xpath("//div[@id='app']/div/div/div/div/div[2]/div/div/div[2]/div[5]").click()
                except:
                    #try to dismiss newletter signup popup with built in selenium class
                    try:
                        driver.find_element_by_xpath("//div[@class='leadinModal-content']//button[1]").click()
                        logging.warning("Passed a row in the TCO crawler due to an exception.")
                        print("Passed a row in the TCO crawler due to an exception.")
                    except Exception as Argument:
                        logging.exception()
                        continue
                        
            
                #driver.find_element_by_xpath('//*[contains(text(), "Close")]').click()
                # for cell in row.find_elements_by_tag_name('td'):
                #     print(cell.text)
        elif label=="EPEAT":
            ##EPEAT inclued placeholder pages for product categories they dont have yet. These are not searchable. Skip these with a continue.
            try:
                driver.find_element_by_xpath("//button[text()='Search']").click()
                element = driver.current_url
                product_pages_list.append([page[0], element])
            except:
                continue
        else:
            elements = None
        if label != "EPEAT":
            for element in elements:
                if label =="TCO":
                    product_pages_list.append([page[0], element])
                else:
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
        elif label == "BA":
            name = driver.find_element_by_xpath("//h1[@class='m-bep_productdetail__title']").text
            category = page[0]
            product_details_list.append([category, name])
        elif label == "TCO":
            name = driver.find_element_by_xpath("//table/tbody/tr[1]/td[2]").text + " " + driver.find_element_by_xpath("//table/tbody/tr[2]/td[2]").text
            category = page[0]
            product_details_list.append([category, name])
        elif label == "EPEAT":
            #print(driver.find_element_by_xpath("//a[@class='link-icon -export']").get_attribute('href'))
            names = excelHandlerEPEAT(driver.find_element_by_xpath("//a[@class='link-icon -export']").get_attribute('href'))
            for index, row in names.iterrows():
                category = page[0]
                product_details_list.append([category, row['Manufacturer'] + " " + row['Product Name']])
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

# ##Blue Angel
# label ="BA"
# getWebsite(label)
# BA_Categories=getCategories(label)
# #print(BA_Categories)
# BA_Category_Pages = getCategoryPages(BA_Categories, label)
# #print(BA_Category_Pages)
# BA_Product_Pages=getProductPages(BA_Category_Pages, label)
# #print(BA_Product_Pages)
# BA_Product_Details=getProductDetails(BA_Product_Pages, label)
# #print(BA_Product_Details)

# ##Write Blue Angel products to csv file
# df = pd.DataFrame(BA_Product_Details)
# df.columns = ['Category', 'Product']
# df['Label'] = "Blue Angel"
# df.to_csv(file_path+"/product_database.csv", mode='a', header= False, index=False, encoding="utf-8")

##TCO Certified
# label ="TCO"
# getWebsite(label)
# TCO_Categories=getCategories(label)
# print(TCO_Categories)
# TCO_Category_Pages = getCategoryPages(TCO_Categories, label)
# print(TCO_Category_Pages)
# TCO_Product_Pages=getProductPages(TCO_Category_Pages, label)
# print(TCO_Product_Pages)
# TCO_Product_Details=getProductDetails(TCO_Product_Pages, label)
# print(TCO_Product_Details)

# # ##Write TCO products to csv file
# df = pd.DataFrame(TCO_Product_Details)
# df.columns = ['Category', 'Product']
# df['Label'] = "TCO Certified"
# df.to_csv(file_path+"/product_database.csv", mode='a', header= False, index=False, encoding="utf-8")

## EPEAT

label ="EPEAT"
getWebsite(label)
EPEAT_Categories=getCategories(label)
print(EPEAT_Categories)
EPEAT_Category_Pages = getCategoryPages(EPEAT_Categories, label)
print(EPEAT_Category_Pages)
EPEAT_Product_Pages=getProductPages(EPEAT_Category_Pages, label)
print(EPEAT_Product_Pages)
EPEAT_Product_Details=getProductDetails(EPEAT_Product_Pages, label)
print(EPEAT_Product_Details)

# # ##Write TCO products to csv file
df = pd.DataFrame(EPEAT_Product_Details)
df.columns = ['Category', 'Product']
df['Label'] = "EPEAT"
df.to_csv(file_path+"/product_database.csv", mode='a', header= False, index=False, encoding="utf-8")


print("finished executing")
driver.close()
