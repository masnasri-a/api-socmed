import requests
from typing import Dict, Any

class TwitterService:
    def __init__(self, api_key: str):
        self.base_url = "https://twitter241.p.rapidapi.com"
        self.headers = {
            "x-rapidapi-key": api_key,
            "x-rapidapi-host": "twitter241.p.rapidapi.com"
        }
    
    def search(self, query: str, search_type: str = "Top", count: int = 20) -> Dict[str, Any]:
        """
        Search Twitter for tweets
        
        Args:
            query: Search query string
            search_type: Type of search (Top, Latest, etc.)
            count: Number of results to return
            
        Returns:
            Dict containing search results
        """
        url = f"{self.base_url}/search-v2"
        querystring = {
            "type": search_type,
            "count": str(count),
            "query": query
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=querystring)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Twitter API error: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}")
    