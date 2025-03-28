import os
import json
import re
from bs4 import BeautifulSoup


def convert_html_to_json(html_dir="html_pages", output_file="posts.json"):
    """Convert HTML files in html_pages directory to JSON format
    
    Args:
        html_dir (str): Directory containing HTML files
        output_file (str): Output JSON file path
    
    Returns:
        int: Number of posts converted
    """
    # Check if directory exists
    if not os.path.exists(html_dir):
        print(f"Directory {html_dir} does not exist!")
        return 0
    
    # Get all HTML files
    html_files = [f for f in os.listdir(html_dir) if f.endswith('.html')]
    
    if not html_files:
        print(f"No HTML files found in {html_dir}!")
        return 0
    
    print(f"Found {len(html_files)} HTML files to convert")
    
    # List to store all converted pages
    all_posts = []
    
    for html_file in html_files:
        try:
            # Extract title from filename (remove .html extension)
            title = os.path.splitext(html_file)[0]
            
            # Create slug from title
            slug = title.lower().replace(' ', '-')
            # Remove any special characters from slug
            slug = re.sub(r'[^a-z0-9-]', '', slug)
            
            # Read HTML file
            with open(os.path.join(html_dir, html_file), 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Process the content into rich text JSON format
            content_nodes = []
            
            # Process all top-level elements
            top_elements = soup.find_all(recursive=False)
            
            for element in top_elements:
                node = process_element(element)
                if node:
                    content_nodes.append(node)
            
            # Create post object
            post = {
                "Title": title,
                "Slug": slug,
                "Content": {
                    "type": "doc",
                    "content": content_nodes
                }
            }
            
            all_posts.append(post)
            print(f"Converted {html_file} to JSON")
            
        except Exception as e:
            print(f"Error converting {html_file}: {e}")
    
    # Save all posts to a JSON file
    with open(output_file, "w", encoding='utf-8') as f:
        json.dump(all_posts, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(all_posts)} posts to {output_file}")
    return len(all_posts)


def process_element(element):
    """Process an HTML element into rich text JSON format"""
    if element.name in ['div', 'p']:
        # Process as paragraph
        return process_paragraph(element)
    elif element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
        # Process as heading
        return process_heading(element)
    elif element.name == 'ul':
        # Process as bullet list
        return process_list(element, 'bullet_list')
    elif element.name == 'ol':
        # Process as ordered list
        return process_list(element, 'ordered_list')
    elif element.name == 'li':
        # Process as list item
        return process_list_item(element)
    elif element.name == 'br':
        # Process as hard break
        return {"type": "hard_break"}
    else:
        # For other elements, try to process their children
        return None


def process_paragraph(element):
    """Process a paragraph element into rich text JSON format"""
    content = []
    
    # Process spans within the paragraph
    spans = element.find_all('span', recursive=False)
    if spans:
        for span in spans:
            content.extend(process_text(span))
    else:
        # If no spans, process the text directly
        content.extend(process_text(element))
    
    # Get alignment from style attribute
    style = element.get('style', '')
    attrs = {}
    
    # Extract text-align attribute
    align_match = re.search(r'text-align:\s*([^;]+)', style)
    if align_match:
        attrs['textAlign'] = align_match.group(1).strip()
    
    return {
        "type": "paragraph",
        "attrs": attrs if attrs else {},
        "content": content
    }


def process_heading(element):
    """Process a heading element into rich text JSON format"""
    level = int(element.name[1])  # Extract the heading level number
    content = []
    
    # Process spans within the heading
    spans = element.find_all('span', recursive=False)
    if spans:
        for span in spans:
            content.extend(process_text(span))
    else:
        # If no spans, process the text directly
        content.extend(process_text(element))
    
    # Get alignment from style attribute
    style = element.get('style', '')
    attrs = {"level": level}
    
    # Extract text-align attribute
    align_match = re.search(r'text-align:\s*([^;]+)', style)
    if align_match:
        attrs['textAlign'] = align_match.group(1).strip()
    
    return {
        "type": "heading",
        "attrs": attrs,
        "content": content
    }


def process_list(element, list_type):
    """Process a list element into rich text JSON format"""
    content = []
    
    # Process list items
    for li in element.find_all('li', recursive=False):
        list_item = process_list_item(li)
        if list_item:
            content.append(list_item)
    
    return {
        "type": list_type,
        "content": content
    }


def process_list_item(element):
    """Process a list item element into rich text JSON format"""
    content = []
    
    # Process paragraph content within the list item
    para = {
        "type": "paragraph",
        "content": []
    }
    
    # Process spans within the list item
    spans = element.find_all('span', recursive=False)
    if spans:
        for span in spans:
            para["content"].extend(process_text(span))
    else:
        # If no spans, process the text directly
        para["content"].extend(process_text(element))
    
    content.append(para)
    
    return {
        "type": "list_item",
        "content": content
    }


def process_text(element):
    """Process text content into rich text JSON format"""
    text_nodes = []
    
    # Get the text content
    text_content = element.get_text()
    if not text_content.strip():
        return text_nodes
    
    # Get style attributes
    style = element.get('style', '')
    marks = []
    
    # Check for bold text
    if element.name == 'strong' or element.name == 'b' or 'font-weight: bold' in style:
        marks.append({"type": "bold"})
    
    # Check for italic text
    if element.name == 'em' or element.name == 'i' or 'font-style: italic' in style:
        marks.append({"type": "italic"})
    
    # Check for underline
    if element.name == 'u' or 'text-decoration: underline' in style:
        marks.append({"type": "underline"})
    
    # Check for font size
    font_size_match = re.search(r'font-size:\s*([^;]+)', style)
    if font_size_match:
        size = font_size_match.group(1).strip()
        marks.append({
            "type": "textStyle",
            "attrs": {"fontSize": size}
        })
    
    # Create the text node
    text_node = {
        "type": "text",
        "text": text_content
    }
    
    # Add marks if any
    if marks:
        text_node["marks"] = marks
    
    text_nodes.append(text_node)
    return text_nodes


if __name__ == "__main__":
    # For direct execution of this file
    convert_html_to_json() 