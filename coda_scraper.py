import requests
import json
import time
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
    
    def get_download_links(self, doc_id: str, pages: List) -> List[str]:
        """Get download links for a list of pages
        
        Args:
            doc_id: The document ID
            pages: A list of [page_id, request_id] pairs
            
        Returns:
            A list of download links
        """
        download_links = []
        
        for i, page in enumerate(pages):
            page_id = page[0]
            request_id = page[1]
            
            print(f"Checking page {i+1}/{len(pages)} (ID: {page_id})...")
            
            try:
                # Get export status
                content = self.get_export_status(doc_id, page_id, request_id)
                
                if content['status'] == 'complete':
                    download_link = content['downloadLink']
                    download_links.append(download_link)
                    print(f"Found download link: {download_link}")
                else:
                    print(f"Page {page_id} export status: {content['status']}")
            except Exception as e:
                print(f"Error checking page {page_id}: {e}")
            
            # Small delay between requests
            time.sleep(1)
            
        return download_links
    
    def filter_pages_by_parent(self, doc_id: str, parent_name: str) -> List:
        """Get all pages with a specific parent name
        
        Args:
            doc_id: The document ID
            parent_name: The name of the parent page
            
        Returns:
            A list of page IDs
        """
        all_pages = self.get_all_doc_pages(doc_id)
        filtered_pages = []
        
        for page in all_pages.get('items', []):
            if page.get('parent') is not None:
                if page['parent'].get('name') == parent_name:
                    filtered_pages.append(page['id'])
        
        return filtered_pages
    
    def initiate_exports(self, doc_id: str, page_ids: List[str]) -> List:
        """Initiate exports for a list of pages
        
        Args:
            doc_id: The document ID
            page_ids: A list of page IDs
            
        Returns:
            A list of [page_id, request_id] pairs
        """
        export_requests = []
        
        for page_id in page_ids:
            try:
                export_response = self.get_page_content(doc_id, page_id)
                request_id = export_response.get('requestId')
                export_requests.append([page_id, request_id])
                print(f"Initiated export for page {page_id}, request ID: {request_id}")
                time.sleep(1)  # Small delay between requests
            except Exception as e:
                print(f"Error initiating export for page {page_id}: {e}")
        
        return export_requests
