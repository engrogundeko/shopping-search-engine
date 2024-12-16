from bs4 import BeautifulSoup
from ...schema import ReviewsResponseSchema, SpecificationsSchema

import json

def extract_product_data(html_content: BeautifulSoup):
    try:
        # Parse the JSON string
        script_tag = html_content.find("script", text=lambda t: "window.__STORE__=" in t)
        if script_tag:
                # Extract the JavaScript content
            js_content = script_tag.string.strip()

            # Remove "window.__STORE__=" prefix and trailing semicolon
            json_data_str = js_content[len("window.__STORE__="):].rstrip(";")
            data = json.loads(json_data_str)

            # Extract the product details
            product_data = data.get("products", [])[0]  # Assuming the first product is of interest

            # Extract fields
            product_details = {
                "name": product_data.get("name"),
                "brand": product_data.get("brand"),
                "price": product_data.get("prices", {}).get("price"),
                "old_price": product_data.get("prices", {}).get("oldPrice"),
                "discount": product_data.get("prices", {}).get("discount"),
                "rating": product_data.get("rating", {}).get("average"),
                "total_ratings": product_data.get("rating", {}).get("totalRatings"),
                "is_shop_express": product_data.get("isShopExpress"),
                "categories": product_data.get("categories"),
                "image_url": product_data.get("image"),
            }

            return product_details

    except (json.JSONDecodeError, KeyError, IndexError) as e:
        print(f"Error parsing JSON: {e}")
        return None


def extract_seller_information(html_content: BeautifulSoup):
        try:
            # Find the seller information section
            # Find the seller information section
            outer_div = html_content.find('div', class_='col4')
            if not outer_div:
                print("Seller information section not found.")
                return None

            outer_section = outer_div.find('section', class_='card')
            if not outer_section:
                print("Seller card section not found.")
                return None

            # Extract seller name
            seller_name = outer_section.select_one(".-hr .-pbs").text.strip() if outer_section.select_one(".-hr .-pbs") else None

            # Extract seller score
            seller_score = outer_section.select_one(".-df .-prxs").text.strip() if outer_section.select_one(".-df .-prxs") else None

            # Extract performance metrics
            performance_details = {}
            performance_rows = outer_section.select(".-bt .-df.-i-ctr")
            for row in performance_rows:
                label = row.select_one("p").text.split(":")[0].strip() if row.select_one("p") else None
                value = row.select_one("span.-m").text.strip() if row.select_one("span.-m") else None
                if label and value:
                    performance_details[label] = value

            # Return collected data
            return {
                "seller_name": seller_name,
                "seller_score": seller_score,
                "performance_details": performance_details
            }


        except Exception as e:
            print(f"An error occurred while fetching seller information: {e}")
            return None


def extract_specifications(html_content: BeautifulSoup) -> SpecificationsSchema:
    """
    Extracts specifications, key features, box contents, ratings, and reviews from the provided HTML content.

    Args:
        html_content (str): The HTML content of the product page.

    Returns:
        dict: A dictionary containing the extracted information.
    """

    # Initialize dictionary to hold the extracted data
    product_details = {
        "key_features": [],
        "box_contents": [],
        "specifications": {},
    }

    # Extract Key Features
    key_features_section = html_content.find("h2", text="Key Features")
    if key_features_section:
        features_list = key_features_section.find_next("ul")
        if features_list:
            product_details["key_features"] = [li.text.strip() for li in features_list.find_all("li")]

    # Extract What's in the Box
    box_contents_section = html_content.find("h2", text="What’s in the box")
    if box_contents_section:
        box_list = box_contents_section.find_next("ul")
        if box_list:
            product_details["box_contents"] = [li.text.strip() for li in box_list.find_all("li")]

    # Extract Specifications
    specifications_section = html_content.find("h2", text="Specifications")
    if specifications_section:
        spec_list = specifications_section.find_next("ul")
        if spec_list:
            for li in spec_list.find_all("li"):
                spec_name = li.find("span", class_="-b")
                if spec_name:
                    key = spec_name.text.strip().strip(":")
                    value = li.text.replace(spec_name.text, "").strip()
                    product_details["specifications"][key] = value
    
    product_info =SpecificationsSchema(**product_details) 
    return product_info

def extract_reviews(html_content: BeautifulSoup) -> ReviewsResponseSchema:
    
    product_reviews = {
            "average_rating": None,
            "total_ratings": 0,
            "rating_breakdown": {},
            "reviews": []
        }


    # Extract Ratings and Reviews
    ratings_section = html_content.find("h2", text="Verified Ratings (56)")
    if ratings_section:
        ratings_container = ratings_section.find_next("div", class_="-fsh0")
        if ratings_container:
            avg_rating = ratings_container.find("span", class_="-b")
            total_ratings = ratings_container.find("p", class_="-fs16")

            if avg_rating and total_ratings:
                product_reviews["average_rating"] = float(avg_rating.text.strip())
                product_reviews["total_ratings"] = int(total_ratings.text.split()[0])

        rating_breakdown_list = html_content.find_all("li", class_="-df")
        for item in rating_breakdown_list:
            stars = item.text[0]
            count = item.find("p", class_="-gy5")
            if count:
                product_reviews["rating_breakdown"][int(stars)] = int(count.text.strip("()"))

        # Extract Reviews
        reviews_section = html_content.find("h2", text="Comments from Verified Purchases(24)")
        if reviews_section:
            reviews_list = reviews_section.find_next("div", class_="cola")
            if reviews_list:
                for article in reviews_list.find_all("article"):
                    review_stars = article.find("div", class_="stars")
                    review_title = article.find("h3")
                    review_body = article.find("p")
                    review_details = article.find("div", class_="-pvs")

                    review_data = {
                        "stars": float(review_stars.text[0]) if review_stars else None,
                        "title": review_title.text.strip() if review_title else None,
                        "content": review_body.text.strip() if review_body else None,
                        "details": review_details.text.strip() if review_details else None
                    }
                    product_reviews["reviews"].append(review_data)
    product_reviews["total_reviews"] = len(product_reviews["reviews"])
    review_info = ReviewsResponseSchema(**product_reviews)
    return review_info

def parse_price(price_str: str) -> float:
    """
    Converts a price string like '₦ 3,850' to a float value.
    Args:
        price_str (str): Price string to convert, e.g., '₦ 3,850'
    Returns:
        float: Parsed float value
    """
    try:
        # Remove currency symbols and commas, then convert to float
        return float(price_str.replace('₦', '').replace(',', '').strip())
    except ValueError:
        # Return 0.0 if conversion fails
        print(f"Failed to parse price from: {price_str}")
        return 0.0

