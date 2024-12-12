from langchain_community.utilities import SearxSearchWrapper
s = SearxSearchWrapper(searx_host="http://localhost:8888")
print(s.run("what is a large language model?")
)

# from urllib.parse import quote

# def test_searxng_with_curl(query, searxng_url="http://localhost:8888", categories=None):
#     import subprocess
#     import json

#     # Encode the query string for safe URL usage
#     encoded_query = quote(query)
#     category_string = "&categories=" + ",".join(categories) if categories else ""
#     url = f"{searxng_url}/search?q={encoded_query}{category_string}&format=json"

#     try:
#         # Run the curl command
#         result = subprocess.run(
#             ["curl", "-s", url],
#             capture_output=True,
#             text=True,
#             check=True,
#         )
#         print(result)
#         return json.loads(result.stdout)
#     except subprocess.CalledProcessError as e:
#         print(f"Error running curl: {e}")
#         return None
#     except json.JSONDecodeError:
#         print("Failed to decode JSON response.")
#         return None




# if __name__ == "__main__":
#     # Test with a local instance and a query
#     response = test_searxng_with_curl(query="Python programming", searxng_url="http://localhost:8888")
    
#     if response:
#         print("Search results:")
#         for result in response.get("results", []):
#             print(f"- {result['title']}: {result['url']}")
#     else:
#         print("No response or an error occurred.")
