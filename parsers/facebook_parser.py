"""
Facebook JSON parser for social media monitoring analytics.
Converts Facebook API responses to Elasticsearch format.
"""

import json
from datetime import datetime
from typing import Dict, List, Any
import re


def parse_facebook_json(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parse Facebook JSON data to Elasticsearch format.
    
    Args:
        data: Facebook API response data
        
    Returns:
        List of documents in Elasticsearch format
    """
    documents = []
    
    # Extract posts from results
    posts = extract_posts_from_data(data)
    
    for post in posts:
        doc = create_post_document(post)
        if doc:
            documents.append(doc)
    
    return documents


def extract_posts_from_data(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract post items from Facebook data structure."""
    posts = []
    
    try:
        # Get results array
        results = data.get('data', {}).get('results', [])
        
        for post in results:
            if post.get('type') == 'post':
                posts.append(post)
                    
    except Exception as e:
        print(f"Error extracting Facebook posts: {e}")
    
    return posts


def create_post_document(post: Dict[str, Any]) -> Dict[str, Any]:
    """Create Elasticsearch document from Facebook post data."""
    try:
        # Extract basic post info
        post_id = post.get('post_id', '')
        message = post.get('message', '')
        message_rich = post.get('message_rich', message)
        url = post.get('url', '')
        
        # Extract timestamp
        timestamp_unix = post.get('timestamp', 0)
        if isinstance(timestamp_unix, (int, float)) and timestamp_unix > 0:
            timestamp = datetime.fromtimestamp(timestamp_unix).isoformat()
        else:
            timestamp = datetime.now().isoformat()
        
        # Extract author information
        author = post.get('author', {})
        user_info = {
            'id': author.get('id', ''),
            'name': author.get('name', ''),
            'url': author.get('url', ''),
            'profile_image_url': author.get('profile_picture_url', '')
        }
        
        # Extract engagement metrics
        reactions = post.get('reactions', {})
        metrics = {
            'reactions_count': post.get('reactions_count', 0),
            'comments_count': post.get('comments_count', 0),
            'shares_count': post.get('reshare_count', 0),
            'like_count': reactions.get('like', 0),
            'love_count': reactions.get('love', 0),
            'wow_count': reactions.get('wow', 0),
            'haha_count': reactions.get('haha', 0),
            'sad_count': reactions.get('sad', 0),
            'angry_count': reactions.get('angry', 0),
            'care_count': reactions.get('care', 0)
        }
        
        # Calculate reaction breakdown percentages
        total_reactions = metrics['reactions_count']
        reaction_breakdown = {}
        if total_reactions > 0:
            for reaction_type, count in reactions.items():
                reaction_breakdown[f'{reaction_type}_percentage'] = round((count / total_reactions) * 100, 2)
        
        # Extract media information
        media_info = extract_media_info(post)
        
        # Extract hashtags and mentions
        hashtags = extract_hashtags(message)
        mentions = extract_mentions(message)
        
        # Extract external links
        external_urls = extract_external_urls(post)
        
        # Determine post type
        post_type = determine_post_type(post)
        
        # Analyze content
        sentiment = analyze_sentiment(message)
        emotions = detect_emotions(message, reactions)
        
        # Calculate engagement rate
        total_engagements = metrics['reactions_count'] + metrics['comments_count'] + metrics['shares_count']
        # Note: Facebook doesn't typically provide reach data in this format, so we can't calculate true engagement rate
        # We'll use reactions + comments + shares as total engagement
        
        # Extract additional metadata
        metadata = {
            'author_title': post.get('author_title'),
            'comments_id': post.get('comments_id', ''),
            'shares_id': post.get('shares_id', ''),
            'text_format_metadata': post.get('text_format_metadata')
        }
        
        # Build the document
        document = {
                'platform': 'facebook',
                'platform_id': post_id,
                'content': message,
                'content_rich': message_rich,
                'author': user_info,
                'timestamp': timestamp,
                'created_timestamp': timestamp_unix,
                'url': url,
                'metrics': metrics,
                'reaction_breakdown': reaction_breakdown,
                'total_engagements': total_engagements,
                'hashtags': hashtags,
                'mentions': mentions,
                'external_urls': external_urls,
                'media_info': media_info,
                'post_type': post_type,
                'sentiment': sentiment,
                'emotions': emotions,
                'language': detect_language(message),
                'metadata': metadata,
                'analyzed_at': datetime.now().isoformat(),
                'raw_data': post
        }
        
        return document
        
    except Exception as e:
        print(f"Error creating Facebook document: {e}")
        return None


def extract_media_info(post: Dict[str, Any]) -> Dict[str, Any]:
    """Extract media information from Facebook post."""
    media_info = {}
    
    # Extract image information
    image = post.get('image')
    if image:
        media_info['image'] = {
            'url': image.get('uri', ''),
            'width': image.get('width', 0),
            'height': image.get('height', 0),
            'id': image.get('id', '')
        }
    
    # Extract video information
    video = post.get('video')
    if video:
        media_info['video'] = {
            'url': video.get('url', ''),
            'thumbnail': video.get('thumbnail', ''),
            'duration': video.get('duration', 0)
        }
    
    # Extract video files
    video_files = post.get('video_files')
    if video_files:
        media_info['video_files'] = video_files
    
    # Extract album preview
    album_preview = post.get('album_preview')
    if album_preview:
        media_info['album_preview'] = album_preview
    
    # Extract video thumbnail
    video_thumbnail = post.get('video_thumbnail')
    if video_thumbnail:
        media_info['video_thumbnail'] = video_thumbnail
    
    return media_info


def extract_hashtags(text: str) -> List[str]:
    """Extract hashtags from Facebook post."""
    if not text:
        return []
    
    hashtag_pattern = r'#(\w+)'
    hashtags = re.findall(hashtag_pattern, text, re.UNICODE)
    return hashtags


def extract_mentions(text: str) -> List[str]:
    """Extract user mentions from Facebook post."""
    if not text:
        return []
    
    mention_pattern = r'@(\w+)'
    mentions = re.findall(mention_pattern, text, re.UNICODE)
    return mentions


def extract_external_urls(post: Dict[str, Any]) -> List[str]:
    """Extract external URLs from Facebook post."""
    urls = []
    
    # Check for external URL field
    external_url = post.get('external_url')
    if external_url:
        urls.append(external_url)
    
    # Check for attached post URL
    attached_post_url = post.get('attached_post_url')
    if attached_post_url:
        urls.append(attached_post_url)
    
    # Extract URLs from message using regex
    message = post.get('message', '')
    if message:
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        found_urls = re.findall(url_pattern, message)
        urls.extend(found_urls)
    
    return urls


def determine_post_type(post: Dict[str, Any]) -> str:
    """Determine the type of Facebook post."""
    # Check for media types
    if post.get('video'):
        return 'video'
    elif post.get('video_files'):
        return 'video'
    elif post.get('image'):
        return 'image'
    elif post.get('album_preview'):
        return 'album'
    elif post.get('external_url'):
        return 'link'
    elif post.get('attached_post'):
        return 'shared_post'
    elif post.get('attached_event'):
        return 'event'
    else:
        return 'text'


def analyze_sentiment(text: str) -> str:
    """Basic sentiment analysis for Facebook content."""
    if not text:
        return 'neutral'
    
    positive_words = ['love', 'amazing', 'great', 'awesome', 'wonderful', 'excellent', 'happy', 'good', 'nice', 'best', 'perfect']
    negative_words = ['hate', 'terrible', 'awful', 'bad', 'worst', 'angry', 'sad', 'disappointed', 'horrible', 'annoying']
    
    text_lower = text.lower()
    
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    if positive_count > negative_count:
        return 'positive'
    elif negative_count > positive_count:
        return 'negative'
    else:
        return 'neutral'


def detect_emotions(text: str, reactions: Dict[str, int]) -> List[str]:
    """Detect emotions from Facebook content and reactions."""
    emotions = []
    
    # Analyze text content
    if text:
        text_lower = text.lower()
        
        emotion_keywords = {
            'joy': ['happy', 'joy', 'excited', 'amazing', 'wonderful', 'celebrate'],
            'love': ['love', 'heart', 'adore', 'beautiful', 'sweet'],
            'anger': ['angry', 'mad', 'furious', 'annoyed', 'frustrated'],
            'sadness': ['sad', 'depressed', 'crying', 'disappointed', 'heartbroken'],
            'surprise': ['wow', 'amazing', 'surprised', 'unbelievable', 'shocking'],
            'fear': ['scared', 'afraid', 'worried', 'anxious', 'terrified'],
            'humor': ['funny', 'hilarious', 'joke', 'comedy', 'lol', 'haha']
        }
        
        for emotion, keywords in emotion_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                emotions.append(emotion)
    
    # Analyze reactions for emotional context
    if reactions:
        total_reactions = sum(reactions.values())
        if total_reactions > 0:
            # If love reactions are dominant, add love emotion
            if reactions.get('love', 0) / total_reactions > 0.3:
                emotions.append('love')
            
            # If haha reactions are dominant, add humor emotion
            if reactions.get('haha', 0) / total_reactions > 0.3:
                emotions.append('humor')
            
            # If angry reactions are significant, add anger emotion
            if reactions.get('angry', 0) / total_reactions > 0.2:
                emotions.append('anger')
            
            # If sad reactions are significant, add sadness emotion
            if reactions.get('sad', 0) / total_reactions > 0.2:
                emotions.append('sadness')
            
            # If wow reactions are dominant, add surprise emotion
            if reactions.get('wow', 0) / total_reactions > 0.3:
                emotions.append('surprise')
    
    return list(set(emotions))  # Remove duplicates


def detect_language(text: str) -> str:
    """Basic language detection for Facebook content."""
    if not text:
        return 'unknown'
    
    # Simple heuristic - check for common words in different languages
    indonesian_words = ['dan', 'yang', 'untuk', 'dengan', 'dari', 'ini', 'itu', 'tidak', 'ada', 'saya', 'kita', 'mereka']
    english_words = ['and', 'the', 'to', 'of', 'a', 'in', 'for', 'is', 'on', 'that', 'you', 'it', 'with', 'as']
    
    text_lower = text.lower()
    
    indonesian_count = sum(1 for word in indonesian_words if f' {word} ' in f' {text_lower} ')
    english_count = sum(1 for word in english_words if f' {word} ' in f' {text_lower} ')
    
    if indonesian_count > english_count:
        return 'id'  # Indonesian
    elif english_count > indonesian_count:
        return 'en'  # English
    else:
        return 'mixed'


def main():
    """Example usage of the parser."""
    # Load example data
    with open('/Volumes/External/Sentimind/socmed-api/example_results/facebook.json', 'r') as f:
        data = json.load(f)
    
    # Parse the data
    documents = parse_facebook_json(data)
    
    print(f"Parsed {len(documents)} documents from Facebook data")
    
    # Save parsed data
    with open('/Volumes/External/Sentimind/socmed-api/parsed_results/facebook_parsed.json', 'w') as f:
        json.dump(documents[:5], f, indent=2, ensure_ascii=False)  # Save first 5 for preview
    
    print("Sample documents saved to facebook_parsed.json")


if __name__ == "__main__":
    main()