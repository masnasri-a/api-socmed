import requests
from typing import Dict, Any

class TikTokService:
    def __init__(self, api_key: str):
        self.base_url = "https://tiktok-api23.p.rapidapi.com"
        self.headers = {
            "x-rapidapi-key": api_key,
            "x-rapidapi-host": "tiktok-api23.p.rapidapi.com"
        }

    def search_general(self, keyword: str, cursor: str = "0", search_id: str = "0") -> Dict[str, Any]:
        """
        Search TikTok for general content

        Args:
            keyword: Search keyword
            cursor: Pagination cursor
            search_id: Search session ID

        Returns:
            Dict containing search results
        """
        url = f"{self.base_url}/api/search/general"
        querystring = {
            "keyword": keyword,
            "cursor": cursor,
            "search_id": search_id
        }

        try:
            response = requests.get(url, headers=self.headers, params=querystring)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"TikTok API error: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}")
