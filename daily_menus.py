import requests
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

def scrape_compass():
    url = "https://www.compass-group.fi/ravintolat-ja-ruokalistat/foodco/kaupungit/espoo/cafe-keilalahti/"
    response = requests.get(url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    menu_items = soup.find_all('div', class_='menu-list-item__meal-name')
    items = [item.get_text(strip=True) for item in menu_items]
    return items

def scrape_sodexo():
    url = "https://www.sodexo.fi/ravintolat/ravintola-foodhub"
    response = requests.get(url)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')
    menu_items = soup.find_all('div', class_='menu-item__title')
    items = [item.get_text(strip=True) for item in menu_items]
    return items

def scrape_iss():
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    driver.get("https://fg.ravintolapalvelut.iss.fi/")
    time.sleep(3)  # Give time for page to load
    try:
        meals = driver.find_elements("class name", "menu-item-title")
        items = [meal.text for meal in meals]
    except Exception:
        items = []
    driver.quit()
    return items

def generate_html(results):
    today = datetime.datetime.now().strftime("%A, %B %d, %Y")

    html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Today's Lunch Menus</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #f8f8f8;
                margin: 0;
                padding: 20px;
            }}
            .container {{
                background: #fff;
                padding: 20px;
                max-width: 800px;
                margin: auto;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
                border-radius: 10px;
            }}
            h1 {{
                color: #2e7d32;
            }}
            h2 {{
                color: #3f51b5;
                margin-top: 30px;
            }}
            ul {{
                padding-left: 20px;
            }}
            li {{
                margin-bottom: 8px;
            }}
            .date {{
                font-size: 1.2em;
                color: #555;
                margin-bottom: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🥗 Today's Lunch Menus</h1>
            <p class="date">📅 {today}</p>
    """

    for restaurant, items in results.items():
        html += f"<h2>{restaurant}</h2>\n<ul>"

        if not items:
            html += "<li>No menu available today.</li>"
        else:
            for item in items:
                try:
                    translated = GoogleTranslator(source='auto', target='en').translate(item)
                    html += f"<li>{translated}</li>"
                except Exception:
                    html += f"<li>{item}</li>"

        html += "</ul>\n"

    html += """
        </div>
    </body>
    </html>
    """

    with open("daily_menus.html", "w", encoding="utf-8") as f:
        f.write(html)

def main():
    print("Scraping today's menus...")
    results = {
        "Food & Co | Cafe Keilahti": scrape_compass(),
        "FoodHub Sodexo": scrape_sodexo(),
        "FG": scrape_iss()
    }
    generate_html(results)
    print("✅ Menus scraped and saved to 'daily_menus.html'!")

if __name__ == "__main__":
    main()

