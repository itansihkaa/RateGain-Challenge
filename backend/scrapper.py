from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from bs4 import BeautifulSoup
import requests
import csv
import os

app = Flask(__name__)
CORS(app)

def scrape_blog_data():
    base_url = "https://rategain.com/blog/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    response = requests.get(base_url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        last_page_number = int(soup.find(class_="pagination").find_all('a', class_='page-numbers')[-2].text)
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        last_page_number = 1  # Assume only one page if failed to get the last page number

    print(f"Total number of pages: {last_page_number}")

    extracted_data = []

    print("Starting to scrape the blog entries...")

    for page_number in range(1, last_page_number + 1):
        print(f"Scraping page {page_number}")
        url = f"{base_url}page/{page_number}/"
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            blog_items = soup.find_all(class_="blog-item")

            for blog_item in blog_items:
                blog_title = blog_item.find(class_="content").find("h6").text.strip()
                blog_date = blog_item.find(class_="blog-detail").find(class_="bd-item").find("span").text.strip()

                img_element = blog_item.find(class_="img")
                if img_element and img_element.find("a") and "data-bg" in img_element.find("a").attrs:
                    blog_img_url = img_element.find("a")["data-bg"]
                else:
                    blog_img_url = None

                like_count = blog_item.find(class_="zilla-likes").find("span").text.strip()

                blog_description = blog_item.find(class_="text").text.split('.')[0].strip()

                blog_entry = {
                    "blog_title": blog_title,
                    "blog_date": blog_date,
                    "blog_img_url": blog_img_url,
                    "like_count": like_count,
                    "blog_description": blog_description
                }
                extracted_data.append(blog_entry)
        else:
            print(f"Failed to retrieve the webpage. Status code: {response.status_code}")

    print("Scraping completed!")

    return extracted_data

@app.route('/scrape', methods=['POST'])
def scrape_endpoint():
    website_link = request.json.get('websiteLink')
    
    # Replace 'data.csv' with your desired file name
    csv_file_path = "data.csv"
    
    extracted_data = scrape_blog_data()
    
    # Writing to CSV file
    with open(csv_file_path, "w", newline="", encoding="utf-8") as csv_file:
        field_names = extracted_data[0].keys() if extracted_data else []
        csv_writer = csv.DictWriter(csv_file, fieldnames=field_names)
        
        if field_names:
            csv_writer.writeheader()
        
        csv_writer.writerows(extracted_data)

    return send_file(csv_file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
