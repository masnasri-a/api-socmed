"""
YouTube JSON parser for social media monitoring analytics.
Converts YouTube API responses to Elasticsearch format.
"""

import json
from datetime import datetime
from typing import Dict, List, Any
import re


def parse_youtube_json(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parse YouTube JSON data to Elasticsearch format.
    
    Args:
        data: YouTube API response data
        
    Returns:
        List of documents in Elasticsearch format
    """
    documents = []
    
    # Extract videos from contents
    videos = extract_videos_from_data(data)
    
    for video in videos:
        doc = create_video_document(video)
        if doc:
            documents.append(doc)
    
    return documents


def extract_videos_from_data(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract video items from YouTube data structure."""
    videos = []
    
    try:
        # Get contents array
        contents = data.get('data', {}).get('contents', [])
        
        for content in contents:
            if content.get('type') == 'video':
                video = content.get('video', {})
                if video:
                    videos.append(video)
                    
    except Exception as e:
        print(f"Error extracting YouTube videos: {e}")
    
    return videos


def create_video_document(video: Dict[str, Any]) -> Dict[str, Any]:
    """Create Elasticsearch document from YouTube video data."""
    try:
        # Extract basic video info
        video_id = extract_video_id(video)
        title = video.get('title', '')
        description = video.get('descriptionSnippet', '')
        
        # Extract author/channel information
        author = video.get('author', {})
        channel_info = {
            'id': author.get('channelId', ''),
            'title': author.get('title', ''),
            'username': author.get('canonicalBaseUrl', '').replace('/@', '') if author.get('canonicalBaseUrl') else '',
            'profile_image_url': get_avatar_url(author.get('avatar', [])),
            'badges': author.get('badges', []),
            'is_verified': is_verified_channel(author.get('badges', []))
        }
        
        # Extract video metrics
        stats = video.get('stats', {})
        metrics = {
            'view_count': stats.get('views', 0),
        }
        
        # Extract video details
        duration_seconds = video.get('lengthSeconds', 0)
        duration_formatted = format_duration(duration_seconds)
        
        # Extract thumbnails
        thumbnails = extract_thumbnails(video)
        
        # Extract publish time
        published_time = video.get('publishedTimeText', '')
        timestamp = parse_youtube_timestamp(published_time)
        
        # Extract badges/labels
        badges = video.get('badges', [])
        
        # Check if live
        is_live = video.get('isLiveNow', False)
        
        # Extract moving thumbnails (GIFs)
        moving_thumbnails = video.get('movingThumbnails', [])
        
        # Analyze content
        full_content = f"{title} {description}"
        sentiment = analyze_sentiment(full_content)
        emotions = detect_emotions(full_content)
        
        # Extract hashtags and mentions
        hashtags = extract_hashtags(description)
        mentions = extract_mentions(description)
        
        # Determine content category
        category = determine_category(title, description)
        
        # Generate video URL
        video_url = f"https://www.youtube.com/watch?v={video_id}" if video_id else ""
        
        # Build the document
        document = {
                'platform': 'youtube',
                'platform_id': video_id,
                'content': full_content,
                'title': title,
                'description': description,
                'author': channel_info,
                'timestamp': timestamp,
                'published_time_text': published_time,
                'url': video_url,
                'metrics': metrics,
                'duration_seconds': duration_seconds,
                'duration_formatted': duration_formatted,
                'thumbnails': thumbnails,
                'moving_thumbnails': moving_thumbnails,
                'badges': badges,
                'is_live': is_live,
                'hashtags': hashtags,
                'mentions': mentions,
                'sentiment': sentiment,
                'emotions': emotions,
                'category': category,
                'language': detect_language(full_content),
                'content_type': 'video',
                'analyzed_at': datetime.now().isoformat(),
                'raw_data': video
            }
        
        return document
        
    except Exception as e:
        print(f"Error creating YouTube document: {e}")
        return None


def extract_video_id(video: Dict[str, Any]) -> str:
    """Extract video ID from various possible locations in the response."""
    # Try to get from videoId field
    video_id = video.get('videoId', '')
    
    if not video_id:
        # Try to extract from navigationEndpoint
        nav_endpoint = video.get('navigationEndpoint', {})
        watch_endpoint = nav_endpoint.get('watchEndpoint', {})
        video_id = watch_endpoint.get('videoId', '')
    
    if not video_id:
        # Try to extract from link or URL fields
        link = video.get('link', '')
        if 'watch?v=' in link:
            video_id = link.split('watch?v=')[1].split('&')[0]
    
    return video_id


def get_avatar_url(avatar_list: List[Dict[str, Any]]) -> str:
    """Get the best quality avatar URL from avatar list."""
    if not avatar_list:
        return ''
    
    # Sort by height (descending) to get highest quality
    sorted_avatars = sorted(avatar_list, key=lambda x: x.get('height', 0), reverse=True)
    return sorted_avatars[0].get('url', '') if sorted_avatars else ''


def is_verified_channel(badges: List[Dict[str, Any]]) -> bool:
    """Check if channel is verified based on badges."""
    for badge in badges:
        if badge.get('type') == 'VERIFIED_CHANNEL' or badge.get('text') == 'Verified':
            return True
    return False


def extract_thumbnails(video: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract thumbnail information from video."""
    thumbnails = video.get('thumbnails', [])
    
    # Format thumbnails for consistency
    formatted_thumbnails = []
    for thumb in thumbnails:
        formatted_thumbnails.append({
            'url': thumb.get('url', ''),
            'width': thumb.get('width', 0),
            'height': thumb.get('height', 0)
        })
    
    return formatted_thumbnails


def format_duration(seconds: int) -> str:
    """Format duration seconds to HH:MM:SS or MM:SS format."""
    if seconds == 0:
        return "00:00"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"


def parse_youtube_timestamp(published_time_text: str) -> str:
    """Parse YouTube published time text to ISO format."""
    try:
        # YouTube uses relative times like "1 day ago", "3 weeks ago", etc.
        # This is a simplified conversion - in production you'd want more sophisticated parsing
        
        if not published_time_text:
            return datetime.now().isoformat()
        
        now = datetime.now()
        
        if 'day' in published_time_text:
            # Extract number of days
            days = int(re.findall(r'\d+', published_time_text)[0])
            timestamp = now - datetime.timedelta(days=days)
        elif 'week' in published_time_text:
            # Extract number of weeks
            weeks = int(re.findall(r'\d+', published_time_text)[0])
            timestamp = now - datetime.timedelta(weeks=weeks)
        elif 'month' in published_time_text:
            # Extract number of months (approximate)
            months = int(re.findall(r'\d+', published_time_text)[0])
            timestamp = now - datetime.timedelta(days=months * 30)
        elif 'year' in published_time_text:
            # Extract number of years (approximate)
            years = int(re.findall(r'\d+', published_time_text)[0])
            timestamp = now - datetime.timedelta(days=years * 365)
        elif 'hour' in published_time_text:
            # Extract number of hours
            hours = int(re.findall(r'\d+', published_time_text)[0])
            timestamp = now - datetime.timedelta(hours=hours)
        elif 'minute' in published_time_text:
            # Extract number of minutes
            minutes = int(re.findall(r'\d+', published_time_text)[0])
            timestamp = now - datetime.timedelta(minutes=minutes)
        else:
            timestamp = now
        
        return timestamp.isoformat()
        
    except:
        return datetime.now().isoformat()


def extract_hashtags(text: str) -> List[str]:
    """Extract hashtags from YouTube description."""
    if not text:
        return []
    
    hashtag_pattern = r'#(\w+)'
    hashtags = re.findall(hashtag_pattern, text, re.UNICODE)
    return hashtags


def extract_mentions(text: str) -> List[str]:
    """Extract channel mentions from YouTube description."""
    if not text:
        return []
    
    mention_pattern = r'@(\w+)'
    mentions = re.findall(mention_pattern, text, re.UNICODE)
    return mentions


def determine_category(title: str, description: str) -> str:
    """Determine content category for YouTube video."""
    content = f"{title} {description}".lower()
    
    categories = {
        'music': ['music', 'song', 'audio', 'album', 'artist', 'band', 'cover', 'acoustic', 'lyric'],
        'gaming': ['gaming', 'game', 'gameplay', 'playthrough', 'walkthrough', 'review', 'trailer'],
        'education': ['tutorial', 'how to', 'learn', 'education', 'course', 'lesson', 'guide', 'tips'],
        'entertainment': ['comedy', 'funny', 'humor', 'entertainment', 'show', 'movie', 'film'],
        'vlog': ['vlog', 'daily', 'life', 'routine', 'day in the life', 'personal'],
        'news': ['news', 'breaking', 'report', 'update', 'current events', 'politics'],
        'sports': ['sports', 'football', 'basketball', 'soccer', 'olympics', 'match', 'game'],
        'technology': ['tech', 'technology', 'review', 'unboxing', 'gadget', 'smartphone', 'computer'],
        'cooking': ['cooking', 'recipe', 'food', 'kitchen', 'chef', 'baking', 'meal'],
        'travel': ['travel', 'trip', 'vacation', 'tour', 'destination', 'adventure'],
        'fashion': ['fashion', 'style', 'outfit', 'clothing', 'beauty', 'makeup'],
        'fitness': ['fitness', 'workout', 'exercise', 'health', 'gym', 'training'],
        'diy': ['diy', 'craft', 'handmade', 'build', 'create', 'project'],
        'podcast': ['podcast', 'interview', 'discussion', 'talk', 'conversation']
    }
    
    for category, keywords in categories.items():
        if any(keyword in content for keyword in keywords):
            return category
    
    return 'general'


def analyze_sentiment(text: str) -> str:
    """Basic sentiment analysis for YouTube content."""
    if not text:
        return 'neutral'
    
    positive_words = ['great', 'amazing', 'awesome', 'excellent', 'fantastic', 'wonderful', 'love', 'best', 'perfect', 'incredible']
    negative_words = ['terrible', 'awful', 'horrible', 'worst', 'hate', 'bad', 'disappointing', 'failed', 'disaster']
    
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
    """Basic emotion detection for YouTube content."""
    if not text:
        return []
    
    emotions = []
    text_lower = text.lower()
    
    emotion_keywords = {
        'excitement': ['excited', 'amazing', 'incredible', 'awesome', 'wow'],
        'joy': ['happy', 'joy', 'fun', 'cheerful', 'delighted'],
        'love': ['love', 'adore', 'beautiful', 'gorgeous', 'wonderful'],
        'curiosity': ['discover', 'explore', 'learn', 'find out', 'reveal'],
        'inspiration': ['inspired', 'motivate', 'achieve', 'success', 'dream'],
        'humor': ['funny', 'hilarious', 'comedy', 'joke', 'laugh'],
        'surprise': ['surprise', 'unexpected', 'shocking', 'unbelievable'],
        'nostalgia': ['memories', 'nostalgic', 'remember', 'throwback', 'classic']
    }
    
    for emotion, keywords in emotion_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            emotions.append(emotion)
    
    return emotions


def detect_language(text: str) -> str:
    """Basic language detection for YouTube content."""
    if not text:
        return 'unknown'
    
    # Simple heuristic - check for common words in different languages
    indonesian_words = ['dan', 'yang', 'untuk', 'dengan', 'dari', 'ini', 'itu', 'tidak', 'ada', 'saya', 'video', 'channel']
    english_words = ['and', 'the', 'to', 'of', 'a', 'in', 'for', 'is', 'on', 'that', 'video', 'channel', 'subscribe']
    
    text_lower = text.lower()
    
    indonesian_count = sum(1 for word in indonesian_words if word in text_lower)
    english_count = sum(1 for word in english_words if word in text_lower)
    
    if indonesian_count > english_count:
        return 'id'  # Indonesian
    elif english_count > indonesian_count:
        return 'en'  # English
    else:
        return 'mixed'


def main():
    """Example usage of the parser."""
    # Load example data
    with open('/Volumes/External/Sentimind/socmed-api/example_results/youtube.json', 'r') as f:
        data = json.load(f)
    
    # Parse the data
    documents = parse_youtube_json(data)
    
    print(f"Parsed {len(documents)} documents from YouTube data")
    
    # Save parsed data
    with open('/Volumes/External/Sentimind/socmed-api/parsed_results/youtube_parsed.json', 'w') as f:
        json.dump(documents[:5], f, indent=2, ensure_ascii=False)  # Save first 5 for preview
    
    print("Sample documents saved to youtube_parsed.json")


if __name__ == "__main__":
    main()