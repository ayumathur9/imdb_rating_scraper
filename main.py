from bs4 import BeautifulSoup
import requests
import pandas as pd
import json
import time

# URL for IMDb Top 250
url = "https://www.imdb.com/chart/top"

# Add headers to mimic a real browser
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# Step 1:  fetch HTML content
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

movie_data = []

# Step 2:  IMDb table structure
rows = soup.select("tbody.lister-list tr")
if rows:
    print("✅ Found old IMDb table structure...")
    for row in rows:
        title_tag = row.select_one("td.titleColumn a")
        year_tag = row.select_one("td.titleColumn span.secondaryInfo")
        rating_tag = row.select_one("td.imdbRating strong")

        title = title_tag.text.strip() if title_tag else "N/A"
        year = year_tag.text.strip("()") if year_tag else "N/A"
        rating = rating_tag.text.strip() if rating_tag else "N/A"

        movie_data.append({"Title": title, "Year": year, "Rating": rating})

# Step 3: If table not found, check for embedded JSON data
if not movie_data:
    print("⚙️ Trying JSON extraction...")
    script_tag = soup.select_one("script[type='application/ld+json']")
    if script_tag:
        data = json.loads(script_tag.string)
        if "itemListElement" in data:
            for item in data["itemListElement"]:
                title = item["item"]["name"]
                year = item["item"].get("datePublished", "N/A")
                rating = item["item"].get("aggregateRating", {}).get("ratingValue", "N/A")

                movie_data.append({"Title": title, "Year": year, "Rating": rating})

# Step 4: If empty, using Selenium
if not movie_data:
    print("\n❌ IMDb content seems to load dynamically with JavaScript.")
    print("➡️ You can enable Selenium fallback by installing it:")
    print("   pip install selenium webdriver-manager\n")
    print("Then use this code snippet below instead of requests-based scraping:\n")
    print("""
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time

from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://www.imdb.com/chart/top/")
time.sleep(5)

soup = BeautifulSoup(driver.page_source, "html.parser")
driver.quit()

movies = soup.select("li.ipc-metadata-list-summary-item")

movie_data = []
for movie in movies:
    title = movie.select_one("h3.ipc-title__text").text.strip()
    year = movie.select_one("span.cli-title-metadata-item").text.strip()
    rating_tag = movie.select_one("span.ipc-rating-star--rating")
    rating = rating_tag.text.strip() if rating_tag else "N/A"
    movie_data.append({"Title": title, "Year": year, "Rating": rating})

df = pd.DataFrame(movie_data)
df.to_csv("imdb_top_250_movies.csv", index=False)
print("✅ IMDb Top 250 movies saved successfully!")
""")

# Step 5: Save final data (if any found)
if movie_data:
    df = pd.DataFrame(movie_data)
    df.to_csv("imdb_top_250_movies.csv", index=False)
    print(f"\n✅ {len(movie_data)} movies saved to imdb_top_250_movies.csv successfully!")
