import requests
from bs4 import BeautifulSoup

# URL to scrape
url = "http://www.puneapmc.org/rates.aspx"
base_url = "http://www.puneapmc.org/"
html_file_path = r"C:\CEP\agrotech\templates\test.html"

# Get the latest link
def get_latest_link():
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        ul_tags = soup.find_all('ul')
        if len(ul_tags) >= 2:
            second_ul = ul_tags[1]
            first_link = second_ul.find('a')
            if first_link and 'href' in first_link.attrs:
                return first_link['href']
    return None

# Scrape the table data from the link
def scrape_table(link):
    full_url = base_url + link
    response = requests.get(full_url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table')
        return str(table) if table else "<p>No data found</p>"
    return "<p>Failed to fetch data</p>"

# Update HTML file
def update_html_with_data(table_html):
    with open(html_file_path, 'r', encoding="utf-8") as file:
        soup = BeautifulSoup(file, 'html.parser')

    # Replace or insert table inside a placeholder div
    placeholder = soup.find('div', id='apmc-table-placeholder')
    if placeholder:
        placeholder.clear()
        placeholder.append(BeautifulSoup(table_html, 'html.parser'))

    with open(html_file_path, 'w', encoding="utf-8") as file:
        file.write(str(soup.prettify()))

def main():
    latest_link = get_latest_link()
    if latest_link:
        table_html = scrape_table(latest_link)
        update_html_with_data(table_html)
        print("✅ HTML updated with latest APMC table")
    else:
        print("❌ No latest link found")

if __name__ == "__main__":
    main()
