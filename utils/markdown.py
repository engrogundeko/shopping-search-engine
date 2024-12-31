def convert_to_markdown(content: str) -> str:
    """
    Convert raw text content into Markdown format.

    - Adjusts header levels (# -> ##, ## -> ###, etc.).
    - Converts bullet points (- -> *).
    - Handles regular text as-is.

    Args:
        content (str): The raw text input.

    Returns:
        str: The formatted Markdown content.
    """
    lines = content.splitlines()
    markdown_lines = []

    for line in lines:
        stripped_line = line.strip()

        # Handle headers and increment their level
        if stripped_line.startswith("# "):
            markdown_lines.append(f"## {stripped_line[2:].strip()}")
        elif stripped_line.startswith("## "):
            markdown_lines.append(f"### {stripped_line[3:].strip()}")
        elif stripped_line.startswith("### "):
            markdown_lines.append(f"#### {stripped_line[4:].strip()}")
        elif stripped_line.startswith("#### "):
            markdown_lines.append(f"##### {stripped_line[5:].strip()}")
        elif stripped_line.startswith("- "):  # Bullet points
            markdown_lines.append(f"* {stripped_line[2:].strip()}")
        elif stripped_line.isdigit() and lines.index(line) + 1 < len(lines):  # Numbered list
            markdown_lines.append(f"1. {stripped_line}")
        elif stripped_line:  # Regular text
            markdown_lines.append(stripped_line)

    return "\n".join(markdown_lines)
