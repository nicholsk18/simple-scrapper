import requests
from requests import get
from bs4 import BeautifulSoup
# Set up db connection
import mysql.connector

import os
from dotenv import load_dotenv
load_dotenv()
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_PORT = os.getenv('DB_PORT')
DB_DATAABSE = os.getenv('DB_DATAABSE')
SITEMAP_URL = os.getenv('SITEMAP_URL')

mydb = mysql.connector.connect(
  host=DB_HOST,
  user=DB_USER,
  password=DB_PASSWORD,
  port=DB_PORT,
  database=DB_DATAABSE
)

db_connection = mydb.cursor()

db_connection.execute("SELECT * FROM page_sections")
myresult = db_connection.fetchall()


######################################
# Function to get insert list
######################################
def get_text_from_elements(type, page_section, elements, link):
    sql_list = []

    for element in elements:
        insert_row = (type, page_section, element.text, "", link)
        sql_list.append(insert_row)

    return sql_list


def search_child_types(page_name, page_section, link):
    type_list = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']
    list = []

    for section in page_section:
        for type in type_list:
            elements = section.findAll(type)
            list.extend(get_text_from_elements(type, page_name, elements, link))

    return list



url = SITEMAP_URL

results = requests.get(url, headers={})

soup = BeautifulSoup(results.text, "html.parser")
# div = soup.find('div', {'class': 'wrap-site'})
# div = soup.find('div', {'class': 'banner'})
xml = soup.findAll('url')

links = []
	
#extract what we need from the url
for element in xml:
    loc = element.find('loc').string
    links.append(loc)

# this will be where the main loop happens

for link in links:
    # insert sql
    sql = "INSERT INTO page_sections (element, page_section, text, page_name, page_url) VALUES (%s, %s, %s, %s, %s)"

    page = requests.get(link, headers={})

    page_document = BeautifulSoup(page.text, "html.parser")

    # Get main site wrapper
    page_body = page_document.find('div', {'class': 'wrap-site'})

    # List of subclasses we need to parse
    # page_sections = ['banner', 'split', 'container', 'faq']
    page_sections = {
        'banner':'div', 
        'split':'div', 
        'container':'div', 
        'faq':'div'
    }

    for html_class in page_sections:
        # get classes tag name
        html_element = page_sections[html_class]

        # for each section look for text
        sub_elements = page_body.findAll(html_element, {'class': html_class})
        sql_insert = search_child_types(html_class, sub_elements, link)
        db_connection.executemany(sql, sql_insert)
        mydb.commit()


    # for each section look for text
    # banner = page_body.findAll('div', {'class': 'banner'})
    # sql_insert = search_child_types('banner', banner, link)
    # db_connection.executemany(sql, sql_insert)
    # mydb.commit()
    # split = page_body.findAll('div', {'class': 'split'})
    # sql_insert = search_child_types('split', split, link)
    # db_connection.executemany(sql, sql_insert)
    # mydb.commit()
    # container = page_body.findAll('div', {'class': 'container'})
    # sql_insert = search_child_types('container', container, link)
    # db_connection.executemany(sql, sql_insert)
    # mydb.commit()
    # faq = page_body.findAll('div', {'class': 'faq'})
    # sql_insert = search_child_types('faq', faq, link)
    # db_connection.executemany(sql, sql_insert)
    # mydb.commit()



# for testing
# link = links[5]

