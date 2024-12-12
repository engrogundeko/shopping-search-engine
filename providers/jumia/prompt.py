def rerank_prompt(context) -> str:
    prompt = f"""
    You are an intelligent assistant tasked with filtering a list of items to return the most relevant results based on a user query. The user query specifies their preferences, and your task is to find items that closely match or are relevant to the query.

    - Input:
      - A **user query**: A string describing the desired items (e.g., "best iPhone phones").
      - A **list of items**: A collection of dictionaries, each representing an item with attributes like name, category, features, and specifications.

    - Output:
      - A filtered list of items that match or are relevant to the query, ranked by relevance.

    - Guidelines:
      1. Analyze the query to extract key terms and phrases.
      2. Compare the query terms with the attributes of each item (e.g., name, features, category).
      3. Include only items that are highly relevant to the query.
      4. Rank the results based on how well they match the user's query.
      5. Return the filtered list, ensuring that only the most relevant items are included.

    **Example:**
    ```json
    {{
      "user_query": "best iPhone phones",
      "items": [
        {{"name": "iPhone 14 Pro"}},
        {{"name": "Samsung Galaxy S22"}},
        {{"name": "iPhone SE (2022)"}},
        {{"name": "OnePlus 10 Pro"}}
      ],
      "expected_output": [
        {{"name": "iPhone 14 Pro"}},
        {{"name": "iPhone SE (2022)"}}]
    }}
    ```

    Context to Analyze:
    {context}
    """ 

    return prompt




    
