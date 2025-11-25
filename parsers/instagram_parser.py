"""
Instagram JSON parser for social media monitoring analytics.
Converts Instagram API responses to Elasticsearch format.
"""

import json
from datetime import datetime
from typing import Dict, List, Any
import re


def parse_instagram_json(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parse Instagram JSON data to Elasticsearch format.
    
    Args:
        data: Instagram API response data
        
    Returns:
        List of documents in Elasticsearch format
    """
    documents = []
    
    # Extract media from different sections
    media_items = extract_media_from_grid(data)
    
    for media in media_items:
        doc = create_media_document(media)
        if doc:
            documents.append(doc)
    
    return documents


def extract_media_from_grid(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract media items from Instagram media grid data structure."""
    media_items = []
    
    try:
        media_grid = data.get('data', {}).get('media_grid', {})
        sections = media_grid.get('sections', [])
        
        for section in sections:
            layout_content = section.get('layout_content', {})
            
            # Handle clips sections
            if 'one_by_two_item' in layout_content:
                clips = layout_content['one_by_two_item'].get('clips', {})
                items = clips.get('items', [])
                for item in items:
                    media = item.get('media', {})
                    if media:
                        media_items.append(media)
            
            # Handle two_by_two sections
            elif 'two_by_two_items' in layout_content:
                two_by_two = layout_content['two_by_two_items']
                for item in two_by_two:
                    media = item.get('media', {})
                    if media:
                        media_items.append(media)
            
            # Handle medias array
            elif 'medias' in layout_content:
                medias = layout_content['medias']
                for media in medias:
                    media_items.append(media)
                    
    except Exception as e:
        print(f"Error extracting Instagram media: {e}")
    
    return media_items


def create_media_document(media: Dict[str, Any]) -> Dict[str, Any]:
    """Create Elasticsearch document from Instagram media data."""
    try:
        # Extract basic media info
        media_id = media.get('id', media.get('pk', ''))
        media_code = media.get('code', '')
        
        # Extract caption
        caption = extract_caption(media)
        
        # Extract user information
        user = media.get('user', {})
        if not user:
            # Try alternative user path
            user = media.get('owner', {})
        
        user_info = {
            'id': str(user.get('pk', user.get('id', ''))),
            'username': user.get('username', ''),
            'display_name': user.get('full_name', user.get('name', '')),
            'followers_count': user.get('follower_count', 0),
            'following_count': user.get('following_count', 0),
            'verified': user.get('is_verified', False),
            'profile_image_url': user.get('profile_pic_url', ''),
            'is_private': user.get('is_private', False),
            'is_business': user.get('is_business_account', False),
            'biography': user.get('biography', '')
        }
        
        # Extract timestamps
        taken_at = media.get('taken_at', media.get('device_timestamp', 0))
        if isinstance(taken_at, (int, float)):
            timestamp = datetime.fromtimestamp(taken_at).isoformat()
        else:
            timestamp = datetime.now().isoformat()
        
        # Extract engagement metrics
        metrics = {
            'like_count': media.get('like_count', 0),
            'comment_count': media.get('comment_count', 0),
            'play_count': media.get('play_count', 0),
            'repost_count': media.get('media_repost_count', 0),
            'share_count': media.get('reshare_count', 0)
        }
        
        # Extract media type and URLs
        media_type = determine_media_type(media)
        media_urls = extract_media_urls(media)
        
        # Extract hashtags and mentions
        hashtags = extract_hashtags(caption)
        mentions = extract_mentions(caption)
        
        # Extract location data
        location = extract_location(media)
        
        # Determine if it's a video or image
        is_video = media_type in ['clips', 'video', 'reel']
        
        # Extract video-specific data
        video_data = {}
        if is_video:
            video_data = {
                'duration': media.get('video_duration', 0),
                'view_count': media.get('view_count', 0),
                'play_count': media.get('play_count', 0),
                'has_audio': media.get('has_audio', True)
            }
        
        # Analyze content
        sentiment = analyze_sentiment(caption)
        emotions = detect_emotions(caption)
        
        # Build the document
        document = {
                'platform': 'instagram',
                'platform_id': str(media_id),
                'content': caption,
                'author': user_info,
                'timestamp': timestamp,
                'metrics': metrics,
                'hashtags': hashtags,
                'mentions': mentions,
                'media_type': media_type,
                'media_urls': media_urls,
                'is_video': is_video,
                'video_data': video_data,
                'location': location,
                'sentiment': sentiment,
                'emotions': emotions,
                'has_liked': media.get('has_liked', False),
                'can_see_insights_as_brand': media.get('can_see_insights_as_brand', False),
                'code': media_code,
                'filter_type': media.get('filter_type', 0),
                'lng': media.get('lng'),
                'lat': media.get('lat'),
                'analyzed_at': datetime.now().isoformat(),
                'raw_data': media
        }
        
        return document
        
    except Exception as e:
        print(f"Error creating Instagram document: {e}")
        return None


def extract_caption(media: Dict[str, Any]) -> str:
    """Extract caption text from Instagram media."""
    caption = ""
    
    # Try different caption paths
    if 'caption' in media:
        caption_obj = media['caption']
        if isinstance(caption_obj, dict):
            caption = caption_obj.get('text', '')
        else:
            caption = str(caption_obj) if caption_obj else ''
    
    # Try edge_media_to_caption
    elif 'edge_media_to_caption' in media:
        edges = media['edge_media_to_caption'].get('edges', [])
        if edges:
            caption = edges[0].get('node', {}).get('text', '')
    
    # Try accessibility_caption as fallback
    elif 'accessibility_caption' in media:
        caption = media['accessibility_caption']
    
    return caption


def determine_media_type(media: Dict[str, Any]) -> str:
    """Determine the type of Instagram media."""
    # Check for video indicators
    if media.get('video_duration') or media.get('is_video') or 'video_url' in media:
        return 'video'
    
    # Check media type field
    media_type = media.get('media_type')
    if media_type == 1:
        return 'image'
    elif media_type == 2:
        return 'video'
    elif media_type == 8:
        return 'carousel'
    
    # Check typename
    typename = media.get('__typename', '')
    if 'Video' in typename:
        return 'video'
    elif 'Image' in typename:
        return 'image'
    
    # Check for clips
    if 'clips' in str(media).lower():
        return 'clips'
    
    # Default to image
    return 'image'


def extract_media_urls(media: Dict[str, Any]) -> List[Dict[str, str]]:
    """Extract media URLs from Instagram media."""
    urls = []
    
    # Image URLs
    if 'image_versions2' in media:
        candidates = media['image_versions2'].get('candidates', [])
        for candidate in candidates:
            urls.append({
                'type': 'image',
                'url': candidate.get('url', ''),
                'width': candidate.get('width', 0),
                'height': candidate.get('height', 0)
            })
    
    # Video URLs
    if 'video_versions' in media:
        for version in media['video_versions']:
            urls.append({
                'type': 'video',
                'url': version.get('url', ''),
                'width': version.get('width', 0),
                'height': version.get('height', 0),
                'type_name': version.get('type', '')
            })
    
    # Single image URL
    elif 'display_url' in media:
        urls.append({
            'type': 'image',
            'url': media['display_url'],
            'width': media.get('dimensions', {}).get('width', 0),
            'height': media.get('dimensions', {}).get('height', 0)
        })
    
    return urls


def extract_hashtags(text: str) -> List[str]:
    """Extract hashtags from Instagram caption."""
    if not text:
        return []
    
    hashtag_pattern = r'#(\w+)'
    hashtags = re.findall(hashtag_pattern, text, re.UNICODE)
    return hashtags


def extract_mentions(text: str) -> List[str]:
    """Extract user mentions from Instagram caption."""
    if not text:
        return []
    
    mention_pattern = r'@(\w+)'
    mentions = re.findall(mention_pattern, text, re.UNICODE)
    return mentions


def extract_location(media: Dict[str, Any]) -> Dict[str, Any]:
    """Extract location data from Instagram media."""
    location = {}
    
    # Check location object
    if 'location' in media and media['location']:
        loc = media['location']
        location = {
            'id': loc.get('pk', ''),
            'name': loc.get('name', ''),
            'short_name': loc.get('short_name', ''),
            'address': loc.get('address', ''),
            'city': loc.get('city', ''),
            'lng': loc.get('lng'),
            'lat': loc.get('lat')
        }
    
    # Check for direct coordinates
    elif 'lng' in media and 'lat' in media:
        location = {
            'lng': media['lng'],
            'lat': media['lat']
        }
    
    return location


def analyze_sentiment(text: str) -> str:
    """Basic sentiment analysis for Instagram content."""
    if not text:
        return 'neutral'
    
    positive_words = ['love', 'amazing', 'beautiful', 'perfect', 'awesome', 'great', 'happy', 'good']
    negative_words = ['bad', 'terrible', 'awful', 'hate', 'angry', 'sad', 'disappointed', 'worst']
    
    text_lower = text.lower()
    
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    if positive_count > negative_count:
        return 'positive'
    elif negative_count > positive_count:
        return 'negative'
    else:
        return 'neutral'


def detect_emotions(text: str) -> List[str]:
    """Basic emotion detection for Instagram content."""
    if not text:
        return []
    
    emotions = []
    text_lower = text.lower()
    
    emotion_keywords = {
        'joy': ['happy', 'joy', 'excited', 'amazing', 'wonderful', 'love'],
        'love': ['love', 'heart', 'adore', 'crush', '❤️', '💕', '💖'],
        'excitement': ['excited', 'wow', 'amazing', 'incredible', 'awesome'],
        'gratitude': ['thank', 'grateful', 'blessed', 'appreciate'],
        'inspiration': ['inspired', 'motivation', 'goals', 'dream']
    }
    
    for emotion, keywords in emotion_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            emotions.append(emotion)
    
    return emotions


def main():
    """Example usage of the parser."""
    # Load example data
    with open('/Volumes/External/Sentimind/socmed-api/example_results/instagram.json', 'r') as f:
        data = json.load(f)
    
    # Parse the data
    documents = parse_instagram_json(data)
    
    print(f"Parsed {len(documents)} documents from Instagram data")
    
    # Save parsed data
    with open('/Volumes/External/Sentimind/socmed-api/parsed_results/instagram_parsed.json', 'w') as f:
        json.dump(documents[:5], f, indent=2, ensure_ascii=False)  # Save first 5 for preview
    
    print("Sample documents saved to instagram_parsed.json")


if __name__ == "__main__":
    main()