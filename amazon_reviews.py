# Importing necessary modules
import streamlit as st 
import google.generativeai as genai
import google.ai.generativelanguage as glm
import pandas as pd
# scraping start 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
import re

# Web driver
# chrome_options = Options()
# chrome_options.add_argument("--headless")


def scrape_reviews(url, max_page=2):
    driver = webdriver.Chrome()
    reviews = []

    for page in range(1, max_page + 1):
        print("Page:", page)
        page_url = f'{url}{page}?ie=UTF8&reviewerType=all_reviews&pageNumber={page}'
        driver.get(page_url)

        review_elements = driver.find_elements(By.XPATH, "//div[@data-hook='review']")
        if review_elements:
            for review in review_elements:
                review_data_dict = {}
                review_data_dict['reviewer_name'] = review.find_element(By.XPATH, ".//span[@class='a-profile-name']").text
                review_data_dict['review_date'] = review.find_element(By.XPATH, ".//span[@data-hook='review-date']").text
              
                review_data_dict['rating'] = review.find_element(By.XPATH, ".//i[contains(@class, 'review-rating')]/span").get_attribute('innerText')
                
                # review_data_dict['rating'] = "Rating not found"
                review_data_dict['review_text'] = review.find_element(By.XPATH, ".//span[@data-hook='review-body']").text
                reviews.append(review_data_dict)
        else:
            print(f'NO Reviews Found on Page {page}')
            break

        # Clicking on the next page button
        try:
            next_button = driver.find_element(By.XPATH, "//li[@class='a-last']//a")
            next_button.click()
            WebDriverWait(driver, 10).until(EC.url_changes(page_url))
        except NoSuchElementException:
            print("Next Page not found")
            break
        
    driver.close()

    return reviews

# web_page_url = "https://www.amazon.in/Apple-iPhone-13-128GB-Blue/product-reviews/B09G9BL5CP/ref=cm_cr_arp_d_paging_btm_next_"



# scraping ends here


genai.configure(api_key="AIzaSyCKESnAOIkl8fIqV-KHOUx5pF-ythxJ1Ng")

if _name=='main_':

    st.header("Sentiment Analysis of Reviews")
    # data = st.sidebar.file_uploader("Upload Data File Here", type=['csv'])

    full_link = st.sidebar.text_input("Enter the link Here")
    btn =  st.sidebar.button("start")


    if btn:

        # full_link = "https://www.amazon.in/Apple-iPhone-13-128GB-Blue/product-reviews/B09G9BL5CP/ref=cm_cr_arp_d_paging_btm_next_1?ie=UTF8&reviewerType=all_reviews&pageNumber=1"

        # Define a regular expression pattern to extract the desired part of the link
        pattern = r'(https://www.amazon.in/[^/]+/product-reviews/[^/]+/ref=cm_cr_arp_d_paging_btm_next_)'

        # Use re.search to find the pattern in the link
        match = re.search(pattern, full_link)

        if match:
            extracted_part = match.group(1)
            print(extracted_part)
            amazon_reviews = scrape_reviews(extracted_part)
        else:
            print("Pattern not found in the link.")

        # amazon_reviews = scrape_reviews(web_page_url)

        # print(amazon_reviews)



        data_file = pd.DataFrame(amazon_reviews)
        data_file['date'] = data_file['review_date'].str.extract(r'on (\d+ \w+ \d{4})')
        data_file['date'] = pd.to_datetime(data_file['date'], format='%d %B %Y')
        if data_file is not None:
            # data_file  = pd.read_csv(data)
            # data_file = pd.DataFrame(amazon_reviews)
            Sentiment = []
            for reviews in data_file['review_text']:
             
                # model selection
                model = genai.GenerativeModel('gemini-pro')

                prompt = """ Give the Sentiment analysis of given review only in three words either *POSITIVE👍🏻 or **NEGATIVE* 👎🏻 
                consider one more condition if the review is to larger consider it *spam* """

                response = model.generate_content([prompt, reviews])
                #  st.write(reviews)
                #  st.write(response.text)
                Sentiment.append(response.text)
                #  st.write("===============================================================================")

            data_file['Sentiment'] = Sentiment
            data_file.drop(columns=['review_date'], inplace=True)
            data_file = data_file.sort_values(by='date', ascending=False).reset_index(drop=True)
            st.write(data_file)



    
Overwriting sentiment_analysis.py
 
# https://www.flipkart.com/apple-iphone-15-plus-black-256-gb/product-reviews/itm4b0608e773fc5?pid=MOBGTAGPWKT2VSBB&lid=LSTMOBGTAGPWKT2VSBBYV0FGC&marketplace=FLIPKART
import requests
from bs4 import BeautifulSoup
import pandas as pd


# User-Agent and Accept-Language headers
headers = {
    'User-Agent': 'Use your own user agent',
    'Accept-Language': 'en-us,en;q=0.5'
}
customer_names = []
review_title = []
ratings = []
comments = []

for i in range(1,2):
    # Construct the URL for the current page
    
    url = "https://www.flipkart.com/apple-iphone-15-plus-black-256-gb/product-reviews/itm4b0608e773fc5?pid=MOBGTAGPWKT2VSBB&lid=LSTMOBGTAGPWKT2VSBBYV0FGC&marketplace=FLIPKART&page="+str(i)
   
    # Send a GET request to the page
    page = requests.get(url, headers=headers)

    # Parse the HTML content
    soup = BeautifulSoup(page.content, 'html.parser')

    # Extract customer names
    names = soup.find_all('p', class_='_2NsDsF AwS1CA')
    for name in names:
        customer_names.append(name.get_text())

    # Extract review titles
    title = soup.find_all('p', class_='z9E0IG')
    for t in title:
        review_title.append(t.get_text())

    # Extract ratings
    rat = soup.find_all('div', class_=['XQDdHH Ga3i8K', 'XQDdHH Czs3gR Ga3i8K' , 'XQDdHH Js30Fc Ga3i8K'])
    for r in rat:
        rating = r.get_text()
        if rating:
            ratings.append(rating)
        else:
            ratings.append('0')  # Replace null ratings with 0

    # Extract comments
    cmt = soup.find_all('div', class_='ZmyHeo')
    for c in cmt:
        comment_text = c.div.div.get_text(strip=True)
        comments.append(comment_text)

# Ensure all lists have the same length
min_length = min(len(customer_names), len(review_title), len(ratings), len(comments))
customer_names = customer_names[:min_length]
review_title = review_title[:min_length]
ratings = ratings[:min_length]
comments = comments[:min_length]

# Create a DataFrame from the collected data
data = {
    'Customer Name': customer_names,
    'Review Title': review_title,
    'Rating': ratings,
    'Comment': comments
}

df = pd.DataFrame(data)
df
