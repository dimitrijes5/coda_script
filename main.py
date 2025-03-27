import os
import json
import time
import webbrowser
import re
import html
from bs4 import BeautifulSoup
from coda_scraper import CodaPageScraper

def scrape_coda():
    # Replace with your API token
    API_TOKEN = "36530698-21e4-4dda-87cf-4f2469449fcf"
    DOC_ID = "kNpO-305IT"
    
    # Initialize scraper
    scraper = CodaPageScraper(API_TOKEN)

    # Create html_pages directory if it doesn't exist
    html_dir = "html_pages"
    if not os.path.exists(html_dir):
        os.makedirs(html_dir)
        print(f"Created directory: {html_dir}")

    try:
        # Load pages from the JSON file
        all_pages = json.load(open("pages.json"))
        print(f"Loaded {len(all_pages)} pages from pages.json")
        
        # Get download links for all pages
        download_links = scraper.get_download_links(DOC_ID, all_pages)
        
        # Save all download links to a file
        with open("download_links.txt", "w") as f:
            for link in download_links:
                f.write(f"{link}\n")
        
        print(f"\nFound {len(download_links)} download links. Saved to download_links.txt")
        
        # Ask if user wants to open links in browser
        if download_links:
            response = input("Do you want to open all download links in your browser? (y/n): ")
            if response.lower() == 'y':
                print("Opening download links in browser...")
                for link in download_links:
                    webbrowser.open(link)
                    time.sleep(0.5)  # Small delay between opening tabs
        
    except Exception as e:
        print(f"An error occurred: {e}")


def convert_html_to_json():
    """Convert HTML files in html_pages directory to JSON format"""
    html_dir = "html_pages"
    
    # Check if directory exists
    if not os.path.exists(html_dir):
        print(f"Directory {html_dir} does not exist!")
        return
    
    # Get all HTML files
    html_files = [f for f in os.listdir(html_dir) if f.endswith('.html')]
    
    if not html_files:
        print(f"No HTML files found in {html_dir}!")
        return
    
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
            
            # Extract content
            # This assumes the main content is in a div with class 'page-content'
            # Adjust this selector based on the actual HTML structure
            content_div = soup.select_one('div')
            
            if not content_div:
                print(f"Warning: Could not find content in {html_file}")
                content_html = ""
            else:
                # Convert content to rich text JSON format
                # This is a simplified version - you may need to adjust based on your needs
                content_html = str(content_div)
            
            # Create post object
            post = {
                "Title": title,
                "Slug": slug,
                "Content": {
                    "type": "doc",
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": html.escape(content_html)
                                }
                            ]
                        }
                    ]
                }
            }
            
            all_posts.append(post)
            print(f"Converted {html_file} to JSON")
            
        except Exception as e:
            print(f"Error converting {html_file}: {e}")
    
    # Save all posts to a JSON file
    with open("posts.json", "w", encoding='utf-8') as f:
        json.dump(all_posts, f, indent=2, ensure_ascii=False)
    
    print(f"Saved {len(all_posts)} posts to posts.json")


if __name__ == "__main__":
    convert_html_to_json()