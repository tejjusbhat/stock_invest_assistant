import requests
from bs4 import BeautifulSoup
import json

class NewsExtractor:
    def __init__(self, user_agent=None):
        self.headers = {
            "User-Agent": user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36"
        }

    def get_news_data(self, query, limit=30):
        # Construct the Google News search URL with query
        url = f"https://www.google.com/search?q={query}&gl=us&tbm=nws&num=100"
        
        # Send a GET request to fetch the page content
        response = requests.get(url, headers=self.headers)
        
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, "html.parser")
        news_results = []

        # Select the relevant container for each news item
        for index, el in enumerate(soup.select("div.SoaBEf")):
            if index >= limit:
                break
            
            news = {
                "link": el.find("a")["href"],
                "title": el.select_one("div.MBeuO").get_text(),
                "snippet": el.select_one(".GI74Re").get_text(),
                "date": el.select_one(".LfVVr").get_text(),
                "source": el.select_one(".NUnG9d span").get_text()
            }
            news_results.append(news)

        # Return the results as a JSON formatted string
        return json.dumps(news_results, indent=2)
    

