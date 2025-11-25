import requests
from typing import Dict, Any, Optional

class FacebookService:
    def __init__(self, api_key: str):
        self.base_url = "https://facebook-scraper3.p.rapidapi.com"
        self.headers = {
            "x-rapidapi-key": api_key,
            "x-rapidapi-host": "facebook-scraper3.p.rapidapi.com"
        }
    
    def search_posts(self, query: str) -> Dict[str, Any]:
        """
        Search Facebook for posts
        
        Args:
            query: Search query string
            
        Returns:
            Dict containing search results
        """
        url = f"{self.base_url}/search/posts"
        querystring = {"query": query}
        
        try:
            response = requests.get(url, headers=self.headers, params=querystring)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Facebook API error: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}")
    