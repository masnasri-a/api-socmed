import requests
from typing import Dict, Any

class YoutubeService:
    def __init__(self, api_key: str):
        self.base_url = "https://youtube138.p.rapidapi.com"
        self.headers = {
            "x-rapidapi-key": api_key,
            "x-rapidapi-host": "youtube138.p.rapidapi.com"
        }
    
    def search(self, query: str, hl: str = "en", gl: str = "US") -> Dict[str, Any]:
        """
        Search YouTube for videos
        
        Args:
            query: Search query string
            hl: Language code
            gl: Geographic location code
            
        Returns:
            Dict containing search results
        """
        url = f"{self.base_url}/search/"
        querystring = {
            "q": query,
            "hl": hl,
            "gl": gl
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=querystring)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"YouTube API error: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}")
    