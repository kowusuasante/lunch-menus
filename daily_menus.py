import requests
from bs4 import BeautifulSoup
from datetime import datetime
from deep_translator import GoogleTranslator

# --- Settings ---
TEST_MODE = False  # Set to True if you want to simulate Monday
FAKE_DATE = datetime(2025, 4, 28)  # Fake Monday, April 28, 2025

# --- URLs for each restaurant ---
RESTAURANTS = {
    "Food & Co | Cafe Keilahi": "https://www.foodandco.fi/en/restaurants/espoo/keilaniemi/cafe-keilaniemi/",
    "FoodHub Sodexo": "https://www.sodexo.fi/ravintolat/espoo/foodhub",
    "FG": "https://www.fgrestaurant.fi/en/lunch/",
}

def get_today_date():
    if TEST_MODE:
        today = FAKE_DATE
    else:
        today = datetime.now()
    return today.strftime("%A, %B %d, %Y")

def scrape_foodandco(url):
    try:
        page = requests.get(url, timeout=10)
        soup = BeautifulSoup(page.content, "html.parser")
        items = soup.select(".menu-item__title")

        menus = [item.get_text(strip=True) for item in items]
        if not menus:
            return ["No menu available today."]
        return menus
    except Exception as e:
        print(f"Error scraping Food&Co: {e}")
        return ["No menu available today."]

def scrape_sodexo(url):
    try:
        page = requests.get(url, timeout=10)
        soup = BeautifulSoup(page.content, "html.parser")
        items = soup.select(".meal-name")

        menus = [item.get_text(strip=True) for item in items]
        if not menus:
            return ["No menu available today."]
        return menus
    except Exception as e:
        print(f"Error scraping Sodexo: {e}")
        return ["No menu available today."]

def scrape_fg(url):
    try:
        page = requests.get(url, timeout=10)
        soup = BeautifulSoup(page.content, "html.parser")
        items = soup.select(".menu-item-content p")

        menus = [item.get_text(strip=True) for item in items]
        if not menus:
            return ["No menu available today."]
        return menus
    except Exception as e:
        print(f"Error scraping FG: {e}")
        return ["No menu available today."]

def translate_menu(menu_list):
    translated = []
    for item in menu_list:
        try:
            translation = GoogleTranslator(source='fi', target='en').translate(item)
            # --- Correction for weird translations ---
            if "Well Menu Available Today" in translation:
                translation = "No menu available today."
            translated.append(translation)
        except Exception as e:
            print(f"Translation error: {e}")
            translated.append(item)
    return translated

def generate_html(menus):
    today_str = get_today_date()
    html = f"""
    <html>
    <head>
        <title>Today's Lunch Menus</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f7f7f7;
                text-align: center;
            }}
            .container {{
                margin: 30px auto;
                padding: 20px;
                background: white;
                border-radius: 10px;
                box-shadow: 0px 0px 10px rgba(0,0,0,0.1);
                max-width: 700px;
            }}
            h1 {{
                color: #2e7d32;
            }}
            h2 {{
                color: #3f51b5;
                margin-top: 30px;
            }}
            ul {{
                list-style-type: disc;
                padding-left: 20px;
                text-align: left;
                display: inline-block;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🥗 Today's Lunch Menus</h1>
            <p>📅 {today_str}</p>
    """

    for restaurant, items in menus.items():
        html += f"<h2>{restaurant}</h2><ul>"
        for item in items:
            html += f"<li>{item}</li>"
        html += "</ul>"

    html += """
        </div>
    </body>
    </html>
    """
    return html

def main():
    menus = {}
    for name, url in RESTAURANTS.items():
        if "foodandco" in url:
            menu = scrape_foodandco(url)
        elif "sodexo" in url:
            menu = scrape_sodexo(url)
        else:
            menu = scrape_fg(url)

        translated_menu = translate_menu(menu)
        menus[name] = translated_menu

    html_content = generate_html(menus)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("✅ index.html generated successfully!")

if __name__ == "__main__":
    main()
