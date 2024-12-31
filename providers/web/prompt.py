from datetime import datetime

date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

information_extractor_prompt = f"""
Restructure and organize plain text extracted from a scraped website into a clean, human-readable Markdown format, following logical and semantic formatting conventions.

## Instructions:

### Input Data:
- The input consists of plain text extracted from a scraped website.
- The text may include content from various sections of the site (e.g., headings, body text, lists, metadata) in an unorganized or jumbled manner.

### Expected Output:
- A well-structured Markdown document with the content organized into meaningful sections and subsections.
- Ensure the formatting adheres to the following Markdown conventions:
  - Use `#` for main headings.
  - Use `##`, `###`, etc., for subheadings to create a hierarchy.
  - Use `-` or `*` for unordered lists.
  - Use numbers for ordered lists.
  - Use `[text](URL)` for hyperlinks.
  - Use `![alt text](image_url)` for images.
  - Use tables formatted with `|` and `---` for tabular data.

### Key Considerations:
- At the beggining of the text, include Source: <URL>, date: <YYYY-MM-DD>, time: <HH:MM:SS>, etc.
- Ignore footer, header, and other non-content sections of the text.
- Identify and logically structure headings, paragraphs, and lists.
- Group related content under appropriate headings or subsections.
- Remove irrelevant or redundant text (e.g., navigation instructions, unrelated content).
- Maintain a natural reading flow with clear distinctions between sections.


### Output Response:
    {{
        content: <Markdown formatted content>,
        valid: <boolean>, if the website has been scraped correctly
    
    }}

### Example for case if the website has not been scraped correctly

    {{
        content: null,
        valid: False
    }}


### Example for case if the website has been scraped correctly
    {{
        content: <Markdown formatted content>,
        valid: True
    }}


## Execution Guidelines:
- Only restructure important parts, ignore header, footer and other info not related to content.
- Analyze the structure of the text and infer logical groupings and hierarchy.
- Format content using appropriate Markdown syntax to enhance readability.
- Keep the output concise and free from unnecessary content.
- Deliverables: Generate a clean Markdown document that organizes the plain text into a well-structured format.

Current date & time in ISO format (UTC timezone) is: {date}.Current date & time in ISO format (UTC timezone) is: {date}.
"""


product_extractor = """

Extract the content from a scraped text of a product page and format it into Markdown.

# Steps

1. **Identify Product Information**: Look for key product data such as name, specifications, price, discounts, and reviews within the scraped text.
2. **Convert Headings**: Convert any main headings discovered into Markdown headings using "#" for top-level headings (e.g., product name), "##" for subheadings (e.g., specifications, reviews), and so on.
3. **Format Specifications**: Structure product specifications into a clear list format. Use bullet points for individual specifications and subheadings for categories (e.g., "## Specifications").
4. **Parse Price and Discounts**: Clearly identify and format the price and any discounts or offers using Markdown syntax. Highlight the original price and the discounted price, if applicable.
5. **Extract Reviews**: Summarize customer reviews, formatting each review under a subheading (e.g., "### Customer Reviews") and using bullet points for individual reviews or ratings.
6. **Structure Comparison Data**: If there are comparisons with other products, format them in a table using Markdown tables for clarity.
7. **Handle Quotes**: If there are any quotes from reviews or product descriptions, format them using the Markdown syntax `> quote`.
8. **Check for Consistency**: Review the output to ensure consistent formatting and that all special elements have been converted to the appropriate Markdown syntax.
9. **Add Images**: If there are product images in the scraped text, format them using Markdown images.
10. **Add Links**: Convert any URLs related to product details or purchase links into proper Markdown hyperlinks: `[link text](URL)`.
11. **Add Footnotes**: If there are footnotes in the scraped text, format them using Markdown footnotes.
12. **Add Citations**: If there are citations or references to sources, format them using Markdown citations.

# Output Format
- The output should be a clean, readable Markdown document respecting typical Markdown syntax rules.
- Ensure that headings, lists, links, and other Markdown elements are applied correctly and consistently.

# Example

### Scraped Text
"Product Name: Awesome Laptop\n\nSpecifications:\n- Processor: Intel i7\n- RAM: 16GB\n- Price: $999 (Discounted from $1199)\n\nCustomer Reviews:\n- 'Great performance!' - 5 stars\n- 'Value for money.' - 4 stars\n\nYou can find more information [here](https://example.com)."

### Markdown Output

Awesome Laptop
Specifications
Processor: Intel i7
RAM: 16GB
Price: $999 (Discounted from $1199)
Customer Reviews
'Great performance!' - 5 stars
'Value for money.' - 4 stars

"""