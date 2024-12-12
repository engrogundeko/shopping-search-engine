import httpx

# Base URL for the website's API
BASE_URL = "https://www.jumia.com.ng/catalog"

# Endpoints
PRODUCT_SPECIFICATIONS_ENDPOINT = "/productspecifications/sku/"
PRODUCT_RATINGS_REVIEWS_ENDPOINT = "/productratingsreviews/sku/"

# Function to fetch product specifications
async def fetch_product_specifications(client, product_id):
    url = f"{BASE_URL}{PRODUCT_SPECIFICATIONS_ENDPOINT}{product_id}/"
    try:
        response = await client.get(url, follow_redirects=True)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        # Debug: Print raw response
        print(f"Raw response for specifications: {response.text}")
        
        # Attempt to parse as JSON
        return response.json()
    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred: {e}")
        return None
    except ValueError:
        print(f"Error parsing JSON for specifications. Raw content: {response.text}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Function to fetch product ratings and reviews
async def fetch_product_ratings_reviews(client, product_id):
    url = f"{BASE_URL}{PRODUCT_RATINGS_REVIEWS_ENDPOINT}{product_id}/"
    try:
        response = await client.get(url, follow_redirects=True)
        response.raise_for_status()
        
        # Debug: Print raw response
        print(f"Raw response for reviews: {response.text}")
        
        # Attempt to parse as JSON
        return response.json()
    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred: {e}")
        return None
    except ValueError:
        print(f"Error parsing JSON for reviews. Raw content: {response.text}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Main async function
async def main():
    # Example product IDs to query
    product_ids = ["TE339MP6JTR0KNAFAMZ"]

    async with httpx.AsyncClient() as client:
        for product_id in product_ids:
            # Fetch specifications
            specifications = await fetch_product_specifications(client, product_id)
            print(f"Specifications for Product ID {product_id}:", specifications)

            # Fetch ratings and reviews
            reviews = await fetch_product_ratings_reviews(client, product_id)
            print(f"Ratings and Reviews for Product ID {product_id}:", reviews)

# Run the main function
import asyncio
asyncio.run(main())
