import requests
from typing import Dict, Any

class InstagramService:
    def __init__(self, api_key: str):
        self.base_url = "https://instagram-premium-api-2023.p.rapidapi.com"
        self.headers = {
            "x-rapidapi-key": api_key,
            "x-rapidapi-host": "instagram-premium-api-2023.p.rapidapi.com",
            "x-access-key": api_key
        }
    
    def search(self, query: str) -> Dict[str, Any]:
        """
        Search Instagram for users/posts
        
        Args:
            query: Search query string
            
        Returns:
            Dict containing search results
        """
        url = f"{self.base_url}/v2/search/topsearch"
        querystring = {"query": query}
        
        try:
            response = requests.get(url, headers=self.headers, params=querystring)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Instagram API error: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}")
    