import csv
import requests
from bs4 import BeautifulSoup
import unicodedata

def scrape_page_products(page_url):
    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.67'}
    x = requests.get(page_url)
    soup = BeautifulSoup(x.content, "html.parser")

    products = soup.find_all('div', {'data-component-type': 's-search-result'})

    scraped_data = []
    for product in products:
        try:
            #url = 'https://www.amazon.in' + product.find('a', attrs= {'class' : 'a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal'})['href']
            url = 'https://www.amazon.in' + product.find('a', {'class': 'a-link-normal s-no-outline'})['href']
        except (TypeError, KeyError):
            url = ''

        try:
            name = product.find('span', attrs={'class' : 'a-size-medium a-color-base a-text-normal'}).text.strip()
        except AttributeError:
            name = ''

        try:
            #price = product.find('span', attrs={'class' : 'a-offscreen'}).text.strip()
            price = product.find('span', attrs={'class': 'a-price-whole'}).text.strip()
        except AttributeError:
            price = ''

        try:
            rating = product.find('span', attrs={'class' : 'a-icon-alt'}).text.strip().split(' ')[0]
        except AttributeError:
            rating = ''

        try:
            reviews = product.find('span', attrs={'class' : 'a-size-base s-underline-text'}).text.strip().replace(',', '')
        except AttributeError:
            reviews = ''

        product_info = scrape_product_page(url)

        scraped_data.append({
            'URL': url,
            'Name': name,
            'Price': price,
            'Rating': rating,
            'Reviews': reviews,
            'Description': product_info.get('Description', ''),
            'ASIN': product_info.get('ASIN', ''),
            'Product Description': product_info.get('Product Description', ''),
            'Manufacturer': product_info.get('Manufacturer', '')
        })
    return scraped_data


# Function to scrape additional information from the product page
def scrape_product_page(product_url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.67'}

    response = requests.get(product_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    product_info = {}
    """
    # Scrape product information
    try:
        description = soup.find('div', {'id' : 'productDescription'}).text.strip()
        product_info['Description'] = description
    except AttributeError:
        pass
    """
    try:
        description = ''
        possible_tags = ['div#productDescription', 'div#aplus', 'div#feature-bullets', 'div#descriptionAndDetails']
        for tag in possible_tags:
            description_tag = soup.select_one(tag)
            if description_tag:
                description = description_tag.get_text().strip()
                product_info['Description'] = description
                break
    except AttributeError:
        pass

    try:
        #asin = soup.find('th', string='ASIN').find_next('td').text.strip()
        asin = soup.find('div', {'data-asin': True})['data-asin'].strip()
        product_info['ASIN'] = asin
    except AttributeError:
        pass
    """
    try:
        product_description = soup.find('div', {'id': 'productDescription'}).text.strip()
        product_info['Product Description'] = product_description
    except AttributeError:
        pass
    """
    """
    try:
        product_description = soup.find('div', {'id': 'productDescription'}).get_text().strip()
        product_info['Product Description'] = product_description
    except AttributeError:
        product_description = soup.find('div', {'id': 'aplus'}).get_text().strip()
        product_info['Product Description'] = product_description
    """
    try:
        product_description = ''
        possible_tags = ['div#productDescription', 'div#aplus', 'div#feature-bullets', 'div#descriptionAndDetails']
        for tag in possible_tags:
            description_tag = soup.select_one(tag)
            if description_tag:
                product_description = description_tag.get_text().strip()
                product_info['Product Description'] = product_description
                break
    except AttributeError:
        pass


    try:
        manufa = soup.find('ul', class_="a-unordered-list a-nostyle a-vertical a-spacing-none detail-bullet-list")
        manufa_items = manufa.find_all('li')  # Find all <li> elements inside the <ul> container
        manufacturer = None
        for item in manufa_items:
            if "Manufacturer" in item.text:
                manufacturer = item.find('span', class_="a-list-item").text.strip()
                break
        manufacturer_name = manufacturer.split(':')[1].strip()
        manufacturer_name = manufacturer_name.replace('\u200e\n ', '').strip()
        #manufacturer_name = unicodedata.normalize("NFKD", manufacturer_name)
        #print("Original manufacturer_name:", repr(manufacturer_name))     #This repr() function will display any hidden or special characters in a printable representation, making it easier to spot unexpected characters.
        product_info['Manufacturer'] = manufacturer_name
    except AttributeError:
        pass

    return product_info






# Scrape products from multiple pages
base_url = 'https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_'
pages_to_scrape = 20

all_products = []
for page_number in range(1, pages_to_scrape + 1):
    page_url = base_url + str(page_number)
    print(f"Scraping page {page_number}...")
    scraped_products = scrape_page_products(page_url)
    all_products.extend(scraped_products)

# Save the scraped data to a CSV file
filename = 'scraped_file5.csv'
fieldnames = ['URL', 'Name', 'Price', 'Rating', 'Reviews', 'Description', 'ASIN', 'Product Description', 'Manufacturer']
#fieldnames = ['URL', 'Name', 'Price', 'Rating', 'Reviews']

with open(filename, 'w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(all_products)

print(f"Scraped data saved to {filename}.")