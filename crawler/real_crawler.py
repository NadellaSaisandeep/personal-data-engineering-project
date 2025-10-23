
import requests
from bs4 import BeautifulSoup
import csv
import time
import random
import os


os.makedirs("data/raw", exist_ok=True)
output_path = "data/raw/real_products.csv"

urls = [
    "https://dir.indiamart.com/search.mp?ss=industrial+machinery",
    "https://dir.indiamart.com/search.mp?ss=electronic+components",
    "https://dir.indiamart.com/search.mp?ss=textiles"
]

with open(output_path, "w", newline='', encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Title", "Company", "Price", "Location", "URL"])

    
    for url in urls:
        print(f"Scraping: {url}")
        headers = {
           
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
        except Exception as e:
            print("Request failed:", e)
            continue

        soup = BeautifulSoup(response.text, "html.parser")

       
        products = soup.find_all("div", class_="lst-product")  
        if not products:
          
            products = soup.find_all("div", class_="card") or soup.find_all("div", class_="grid")

        print(f"Found {len(products)} products")

        count = 0
        for p in products:
            
            title = p.find("a", class_="clg") or p.find("a", class_="prd-name")
            company = p.find("span", class_="cmp-name") or p.find("div", class_="cmp_name")
            price = p.find("span", class_="prc") or p.find("span", class_="price")
            location = p.find("span", class_="cmp-loc") or p.find("div", class_="loc")

            title_text = title.get_text(strip=True) if title else ""
            company_text = company.get_text(strip=True) if company else ""
            price_text = price.get_text(strip=True) if price else ""
            location_text = location.get_text(strip=True) if location else ""
            url_link = title['href'] if title and title.has_attr('href') else url

            if title_text:
                writer.writerow([title_text, company_text, price_text, location_text, url_link])
                count += 1

            if count >= 50:
                break

       
        delay = random.uniform(3, 6)
        print(f"Sleeping {delay:.1f}s before next request...")
        time.sleep(delay)

print(" Done! Data saved to", output_path)
