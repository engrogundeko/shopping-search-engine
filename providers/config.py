import asyncio
from .jumia.scrapeng import JumiaScraperNG
from .shopinverse.scrape import ShopInverse

async def get_all_results(search_query) -> list:
    # final_results = []

    # # Create task objects
    # tasks = 
    

    try:
        return await JumiaScraperNG(search_query).run()
        # Run all tasks concurrently and wait for them to complete
        # results = await asyncio.gather(*tasks, return_exceptions=True)
    except Exception as e:
        print(f"Error during task execution: {e}")
        return final_results  # Return empty list in case of an error

    # for result in results:
    #     if isinstance(result, Exception):
    #         print(f"Task failed with exception: {result}")
    #         continue  # Skip to the next result if this one failed

    #     # Process results
    #     if hasattr(result, 'results'):  # Check for ShopProviderResponse
    #         final_results.extend(result.results)
    #     elif isinstance(result, list):
    #         final_results.extend(result)
    #     else:
    #         print(f"Unexpected result type: {type(result)}")
            
    # return final_results

