from bs4 import BeautifulSoup

SHOP_INVERSE_KEY = "?sca_ref=7613147.jv2QpBYyLQyhCa"

def scrape_product_data(html_content: BeautifulSoup):
    """
    Scrapes product details from the provided BeautifulSoup content.
    Extracts:
        - Product title
        - Product image URL
        - Product price
    Args:
        html_content (BeautifulSoup): The parsed HTML content of the page
    Returns:
        list: List of dictionaries with extracted product information
    """
    try:
        # Find all product containers
        products_container = html_content.find_all('li')
        # Initialize an empty list to store extracted product data
        extracted_products = []
        
        for li in products_container:
            # Extract the product name
            product_name_tag = li.select_one('.card__information h3 a')
            product_name = product_name_tag.text.strip() if product_name_tag else 'Not Found'

            # Extract the product URL
            product_url = product_name_tag['href'] if product_name_tag else 'Not Found'

            # Extract the product image URL
            img_tag = li.select_one('img')
            product_image = img_tag['src'] if img_tag else 'Not Found'

            # Extract the price
            price_tag = li.select_one('.price__sale .price-item--sale')
            product_price = price_tag.text.strip() if price_tag else 'Not Found'

            # Append extracted data as a dictionary to the list
            extracted_products.append({
                "product_name": product_name,
                "product_url": product_url,
                "image_url": product_image,
                "price": product_price,
                "product_affiliate_url": get_affiliate_link(product_url)
            })

        # Return all extracted product information
        return extracted_products


    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def get_affiliate_link(product_url):
    return product_url + SHOP_INVERSE_KEY
    
def extract_specification_details(soup: BeautifulSoup) -> dict:

    # Dictionary to store extracted data
    soup = soup.find("div", class_="product__description rte quick-add-hidden")
    details = {}

    # Extract Brand
    brand_tag = soup.find("li", string=lambda x: x and "Brand :" in x)
    details["brand"] = brand_tag.get_text(strip=True).replace("Brand : ", "") if brand_tag else None

    # Extract Model
    model_tag = soup.find("li", string=lambda x: x and "Model :" in x)
    details["model"] = model_tag.get_text(strip=True).replace("Model : ", "") if model_tag else None

    # Extract Processor
    processor_tag = soup.find("li", string=lambda x: x and "Processor :" in x)
    details["processor"] = processor_tag.get_text(strip=True).replace("Processor : ", "") if processor_tag else None

    # Extract RAM
    ram_tag = soup.find("li", string=lambda x: x and "RAM :" in x)
    details["ram"] = ram_tag.get_text(strip=True).replace("RAM : ", "") if ram_tag else None

    # Extract Storage Capacity
    storage_tag = soup.find("li", string=lambda x: x and "Storage Capacity :" in x)
    details["storage"] = storage_tag.get_text(strip=True).replace("Storage Capacity : ", "") if storage_tag else None

    # Extract Maximum Storage Capacity
    max_storage_tag = soup.find("li", string=lambda x: x and "Maximum Storage Capacity :" in x)
    details["max_storage"] = max_storage_tag.get_text(strip=True).replace("Maximum Storage Capacity : ", "") if max_storage_tag else None

    # Extract Display Resolution
    resolution_tag = soup.find("li", string=lambda x: x and "Resolution :" in x)
    details["display_resolution"] = resolution_tag.get_text(strip=True).replace("Resolution : ", "") if resolution_tag else None

    # Extract Battery Backup
    battery_tag = soup.find("li", string=lambda x: x and "Minimum battery backup :" in x)
    details["battery_backup"] = battery_tag.get_text(strip=True).replace("Minimum battery backup : ", "") if battery_tag else None

    return details
