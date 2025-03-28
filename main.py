import os
import json
import time
import webbrowser
import re
from coda_scraper import CodaPageScraper
from html_converter import convert_html_to_json

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


if __name__ == "__main__":
    # Ask user what operation to perform
    print("Select an operation:")
    print("1. Scrape Coda pages")
    print("2. Convert HTML files to JSON")
    
    choice = input("Enter your choice (1 or 2): ")
    
    if choice == "1":
        scrape_coda()
    elif choice == "2":
        convert_html_to_json()
    else:
        print("Invalid choice. Please enter 1 or 2.")