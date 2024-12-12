# Shop Search Engine

The Shop Search Engine is a robust and professional Python-based tool designed to interface with the Shopify API for efficient product search and retrieval. This tool provides advanced features for extracting product data and searching based on specific keywords.

## Features

- **API-Based Data Retrieval**: Fetch comprehensive product data from Shopify stores using their API.
- **Data Validation**: Utilize `pydantic` for rigorous JSON validation and structured data parsing.
- **Keyword Search**: Perform powerful keyword-based searches across product titles and descriptions.
- **Image Handling**: Extract and manage `featured_image` URLs seamlessly.

## Requirements

- Python 3.8 or higher
- `pydantic` for data validation
- `requests` for API communication

Install dependencies using:
```bash
pip install pydantic requests
```

## Setup and Usage

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/shop-search-engine.git
   cd shop-search-engine
   ```

2. **Configure and Run**:
   - Replace `https://examplestore.myshopify.com` with your target Shopify store's URL.
   - Use the following script as an example:

   ```python
   import requests
   from pydantic import BaseModel, ValidationError

   class Product(BaseModel):
       title: str
       body_html: str
       featured_image: str

   def fetch_products(shop_url):
       api_url = f"{shop_url}/products.json"
       response = requests.get(api_url)
       response.raise_for_status()
       return response.json().get('products', [])

   def search_products(products, keyword):
       return [product for product in products if keyword.lower() in product['title'].lower() or keyword.lower() in product['body_html'].lower()]

   # Example Usage
   shop_url = "https://examplestore.myshopify.com"

   try:
       products_data = fetch_products(shop_url)
       products = [Product(**product) for product in products_data]

       keyword = "t-shirt"
       results = search_products(products_data, keyword)

       for product in results:
           print(f"Title: {product.title}\nDescription: {product.body_html}\nImage: {product.featured_image}\n")
   except ValidationError as e:
       print(f"Data validation error: {e}")
   except requests.RequestException as e:
       print(f"API request error: {e}")
   ```

## Project Structure

- `shop_search.py`: Core script for interacting with the Shopify API and performing keyword searches.
- `requirements.txt`: Dependency list for streamlined setup.
- `README.md`: Comprehensive project documentation.

## Important Notes

- Ensure the target Shopify store’s API is publicly accessible; private stores may require authentication.
- Enhance the `search_products` function to support additional filters, such as price or availability.

## Contributing

We welcome contributions to enhance the Shop Search Engine. Please submit an issue or a pull request for suggestions and improvements.

## License

This project is licensed under the MIT License. See the `LICENSE` file for complete details.

---

Effortlessly search and explore Shopify products with the Shop Search Engine! 🚀

