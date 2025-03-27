import requests
import json
import time
import os
import webbrowser
from typing import Dict, Any, List

class CodaPageScraper:
    def __init__(self, api_token: str):
        self.api_token = api_token
        self.base_url = "https://coda.io/apis/v1"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }

    def get_doc(self, doc_id: str) -> Dict[str, Any]:
        """Get a specific document by ID"""
        params = {
            'isOwner': True,
            'query': 'New'
        }
        response = requests.get(f"{self.base_url}/docs/{doc_id}", headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def get_all_docs(self, query_params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get documents with optional filtering"""
        params = {
            'isOwner': True,
            'query': 'New'
        }
        response = requests.get(f"{self.base_url}/docs", headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def get_all_doc_pages(self, doc_id: str) -> Dict[str, Any]:
        """Get all pages of a document"""
        response = requests.get(f"{self.base_url}/docs/{doc_id}/pages", headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_page_content(self, doc_id: str, page_id: str) -> Dict[str, Any]:
        """Get the content of a page"""
        uri = f'https://coda.io/apis/v1/docs/{doc_id}/pages/{page_id}/export'
        payload = {
        'outputFormat': 'html',
        }
        req = requests.post(uri, headers=self.headers, json=payload)
        req.raise_for_status() # Throw if there was an error.
        res = req.json()
        return res

    def get_export_status(self, doc_id: str, page_id: str, request_id: str) -> Dict[str, Any]:
        """Get the export status of a page"""
        uri = f'https://coda.io/apis/v1/docs/{doc_id}/pages/{page_id}/export/{request_id}'
        req = requests.get(uri, headers=self.headers)
        req.raise_for_status() # Throw if there was an error.
        return req.json()

def main():
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
        
        # Store all download links
        download_links = []
        
        # Process each page to get download links
        for i, page in enumerate(all_pages):
            page_id = page[0]
            request_id = page[1]
            
            print(f"Checking page {i+1}/{len(all_pages)} (ID: {page_id})...")
            
            # Get export status
            content = scraper.get_export_status(DOC_ID, page_id, request_id)
            
            if content['status'] == 'complete':
                download_link = content['downloadLink']
                download_links.append(download_link)
                print(f"Found download link: {download_link}")
            else:
                print(f"Page {page_id} export status: {content['status']}")
            
            # Small delay between requests
            time.sleep(1)
        
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
        
    except requests.exceptions.RequestException as e:
        print(f"Error accessing Coda API: {e}")
        # Print the response if available
        if hasattr(e, 'response') and e.response:
            print(f"Response status: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()