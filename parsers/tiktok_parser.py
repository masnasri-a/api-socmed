"""
TikTok JSON parser for social media monitoring analytics.
Converts TikTok API responses to Elasticsearch format.
"""

import json
from datetime import datetime
from typing import Dict, List, Any
import re


def parse_tiktok_json(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parse TikTok JSON data to Elasticsearch format.
    
    Args:
        data: TikTok API response data
        
    Returns:
        List of documents in Elasticsearch format
    """
    documents = []
    
    # Extract videos from data array
    videos = extract_videos_from_data(data)
    
    for video in videos:
        doc = create_video_document(video)
        if doc:
            documents.append(doc)
    
    return documents


def extract_videos_from_data(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract video items from TikTok data structure."""
    videos = []
    
    try:
        # Get data array
        data_array = data.get('data', {}).get('data', [])
        
        for item in data_array:
            if item.get('type') == 1:  # Video type
                video_item = item.get('item', {})
                if video_item:
                    videos.append(video_item)
                    
    except Exception as e:
        print(f"Error extracting TikTok videos: {e}")
    
    return videos


def create_video_document(video: Dict[str, Any]) -> Dict[str, Any]:
    """Create Elasticsearch document from TikTok video data."""
    try:
        # Extract basic video info
        video_id = video.get('id', '')
        desc = video.get('desc', '')
        create_time = video.get('createTime', 0)
        
        # Convert timestamp
        if isinstance(create_time, (int, float)) and create_time > 0:
            timestamp = datetime.fromtimestamp(create_time).isoformat()
        else:
            timestamp = datetime.now().isoformat()
        
        # Extract author information
        author = video.get('author', {})
        user_info = {
            'id': author.get('id', ''),
            'username': author.get('uniqueId', ''),
            'display_name': author.get('nickname', ''),
            'followers_count': author.get('followerCount', 0),
            'following_count': author.get('followingCount', 0),
            'verified': author.get('verified', False),
            'profile_image_url': author.get('avatarLarger', author.get('avatarMedium', '')),
            'signature': author.get('signature', ''),
            'is_private': author.get('privateAccount', False)
        }
        
        # Extract video statistics
        stats = video.get('stats', {})
        metrics = {
            'view_count': stats.get('playCount', 0),
            'like_count': stats.get('diggCount', 0),
            'comment_count': stats.get('commentCount', 0),
            'share_count': stats.get('shareCount', 0),
            'download_count': stats.get('downloadCount', 0),
            'collect_count': stats.get('collectCount', 0)
        }
        
        # Extract video details
        video_info = video.get('video', {})
        video_data = {
            'duration': video_info.get('duration', 0),
            'height': video_info.get('height', 0),
            'width': video_info.get('width', 0),
            'ratio': video_info.get('ratio', ''),
            'bitrate': video_info.get('bitrate', 0),
            'format': video_info.get('format', ''),
            'quality': video_info.get('videoQuality', ''),
            'codec': video_info.get('codecType', ''),
            'cover': video_info.get('cover', ''),
            'dynamic_cover': video_info.get('dynamicCover', ''),
            'play_url': video_info.get('playAddr', ''),
            'download_url': video_info.get('downloadAddr', '')
        }
        
        # Extract music information
        music = video.get('music', {})
        music_info = {
            'id': music.get('id', ''),
            'title': music.get('title', ''),
            'author': music.get('authorName', ''),
            'original': music.get('original', False),
            'duration': music.get('duration', 0),
            'play_url': music.get('playUrl', ''),
            'cover': music.get('coverLarge', music.get('coverMedium', ''))
        }
        
        # Extract hashtags and mentions
        hashtags = extract_hashtags(desc)
        mentions = extract_mentions(desc)
        
        # Extract challenges/effects
        challenges = extract_challenges(video)
        effects = extract_effects(video)
        
        # Analyze content
        sentiment = analyze_sentiment(desc)
        emotions = detect_emotions(desc)
        
        # Determine content category
        category = determine_category(desc, hashtags, music_info)
        
        # Extract engagement rate
        total_engagements = metrics['like_count'] + metrics['comment_count'] + metrics['share_count']
        engagement_rate = (total_engagements / max(metrics['view_count'], 1)) * 100 if metrics['view_count'] > 0 else 0
        
        # Build the document
        document = {
            '_index': 'social_media_posts',
            '_id': f"tiktok_{video_id}",
            '_score': 1.0,
            '_source': {
                'platform': 'tiktok',
                'platform_id': video_id,
                'content': desc,
                'author': user_info,
                'timestamp': timestamp,
                'created_time': create_time,
                'metrics': metrics,
                'video_data': video_data,
                'music_info': music_info,
                'hashtags': hashtags,
                'mentions': mentions,
                'challenges': challenges,
                'effects': effects,
                'sentiment': sentiment,
                'emotions': emotions,
                'category': category,
                'engagement_rate': round(engagement_rate, 2),
                'language': detect_language(desc),
                'is_ad': video.get('isAd', False),
                'duet_enabled': video.get('duetEnabled', True),
                'stitch_enabled': video.get('stitchEnabled', True),
                'comment_enabled': not video.get('commentDisabled', False),
                'analyzed_at': datetime.now().isoformat(),
                'raw_data': video
            }
        }
        
        return document
        
    except Exception as e:
        print(f"Error creating TikTok document: {e}")
        return None


def extract_hashtags(text: str) -> List[str]:
    """Extract hashtags from TikTok description."""
    if not text:
        return []
    
    hashtag_pattern = r'#(\w+)'
    hashtags = re.findall(hashtag_pattern, text, re.UNICODE)
    return hashtags


def extract_mentions(text: str) -> List[str]:
    """Extract user mentions from TikTok description."""
    if not text:
        return []
    
    mention_pattern = r'@(\w+)'
    mentions = re.findall(mention_pattern, text, re.UNICODE)
    return mentions


def extract_challenges(video: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract challenge information from TikTok video."""
    challenges = []
    
    # Check for challenges in video data
    challenges_data = video.get('challenges', [])
    for challenge in challenges_data:
        challenges.append({
            'id': challenge.get('id', ''),
            'title': challenge.get('title', ''),
            'desc': challenge.get('desc', ''),
            'cover': challenge.get('coverLarger', ''),
            'is_commerce': challenge.get('isCommerce', False)
        })
    
    return challenges


def extract_effects(video: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract effects information from TikTok video."""
    effects = []
    
    # Check for effects in video data
    effects_data = video.get('effectStickers', [])
    for effect in effects_data:
        effects.append({
            'id': effect.get('ID', ''),
            'name': effect.get('name', ''),
            'icon': effect.get('iconUrl', ''),
            'owner_id': effect.get('ownerId', ''),
            'owner_username': effect.get('ownerUsername', '')
        })
    
    return effects


def analyze_sentiment(text: str) -> str:
    """Basic sentiment analysis for TikTok content."""
    if not text:
        return 'neutral'
    
    positive_words = ['love', 'amazing', 'fun', 'cool', 'awesome', 'great', 'happy', 'good', 'nice', 'best']
    negative_words = ['bad', 'terrible', 'awful', 'hate', 'angry', 'sad', 'disappointed', 'worst', 'boring']
    
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
    """Basic emotion detection for TikTok content."""
    if not text:
        return []
    
    emotions = []
    text_lower = text.lower()
    
    emotion_keywords = {
        'joy': ['happy', 'joy', 'fun', 'excited', 'amazing', 'wonderful', 'laugh'],
        'love': ['love', 'heart', 'adore', 'crush', '❤️', '💕'],
        'excitement': ['excited', 'wow', 'amazing', 'incredible', 'awesome', 'omg'],
        'humor': ['funny', 'lol', 'haha', 'hilarious', 'joke', 'comedy'],
        'inspiration': ['inspired', 'motivation', 'goals', 'dream', 'believe'],
        'creativity': ['creative', 'art', 'design', 'diy', 'tutorial'],
        'energy': ['energy', 'power', 'strong', 'fierce', 'bold']
    }
    
    for emotion, keywords in emotion_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            emotions.append(emotion)
    
    return emotions


def determine_category(desc: str, hashtags: List[str], music_info: Dict[str, Any]) -> str:
    """Determine content category for TikTok video."""
    text_lower = desc.lower()
    hashtags_lower = [tag.lower() for tag in hashtags]
    
    categories = {
        'dance': ['dance', 'dancing', 'choreography', 'moves', 'dancechallenge'],
        'comedy': ['funny', 'comedy', 'joke', 'humor', 'meme', 'viral', 'hilarious'],
        'education': ['tutorial', 'how', 'learn', 'education', 'tips', 'diy', 'howto'],
        'lifestyle': ['lifestyle', 'daily', 'routine', 'life', 'vlog', 'day'],
        'food': ['food', 'cooking', 'recipe', 'eat', 'delicious', 'foodie'],
        'fashion': ['fashion', 'outfit', 'style', 'clothing', 'ootd', 'fashiontok'],
        'beauty': ['beauty', 'makeup', 'skincare', 'beautytips', 'cosmetics'],
        'fitness': ['fitness', 'workout', 'exercise', 'gym', 'health', 'fit'],
        'music': ['music', 'singing', 'song', 'cover', 'musician', 'musictok'],
        'pets': ['pet', 'dog', 'cat', 'animal', 'cute', 'petsoftiktok'],
        'travel': ['travel', 'trip', 'vacation', 'explore', 'traveltok'],
        'gaming': ['gaming', 'game', 'gamer', 'videogames', 'esports']
    }
    
    # Check hashtags first (more reliable)
    for category, keywords in categories.items():
        if any(keyword in hashtags_lower for keyword in keywords):
            return category
    
    # Check description text
    for category, keywords in categories.items():
        if any(keyword in text_lower for keyword in keywords):
            return category
    
    # Check if it's original music (might be music category)
    if music_info.get('original', False):
        return 'music'
    
    return 'general'


def detect_language(text: str) -> str:
    """Basic language detection for TikTok content."""
    if not text:
        return 'unknown'
    
    # Simple heuristic - check for common words in different languages
    indonesian_words = ['dan', 'yang', 'untuk', 'dengan', 'dari', 'ini', 'itu', 'tidak', 'ada', 'saya']
    english_words = ['and', 'the', 'to', 'of', 'a', 'in', 'for', 'is', 'on', 'that']
    
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
    with open('/Volumes/External/Sentimind/socmed-api/example_results/tiktok.json', 'r') as f:
        data = json.load(f)
    
    # Parse the data
    documents = parse_tiktok_json(data)
    
    print(f"Parsed {len(documents)} documents from TikTok data")
    
    # Save parsed data
    with open('/Volumes/External/Sentimind/socmed-api/parsed_results/tiktok_parsed.json', 'w') as f:
        json.dump(documents[:5], f, indent=2, ensure_ascii=False)  # Save first 5 for preview
    
    print("Sample documents saved to tiktok_parsed.json")


if __name__ == "__main__":
    main()