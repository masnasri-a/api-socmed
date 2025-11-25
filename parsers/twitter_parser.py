"""
Twitter JSON parser for social media monitoring analytics.
Converts Twitter API responses to Elasticsearch format.
"""

import json
from datetime import datetime
from typing import Dict, List, Any
import re


def parse_twitter_json(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parse Twitter JSON data to Elasticsearch format.
    
    Args:
        data: Twitter API response data
        
    Returns:
        List of documents in Elasticsearch format
    """
    documents = []
    
    # Extract tweets from timeline instructions
    tweets = extract_tweets_from_timeline(data)
    
    for tweet in tweets:
        doc = create_tweet_document(tweet)
        if doc:
            documents.append(doc)
    
    return documents


def extract_tweets_from_timeline(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extract tweet objects from Twitter timeline data structure."""
    tweets = []
    
    try:
        timeline = data.get('data', {}).get('result', {}).get('timeline', {})
        instructions = timeline.get('instructions', [])
        
        for instruction in instructions:
            if instruction.get('type') == 'TimelineAddEntries':
                entries = instruction.get('entries', [])
                
                for entry in entries:
                    content = entry.get('content', {})
                    
                    # Handle individual tweet entries
                    if content.get('entryType') == 'TimelineTimelineItem':
                        item_content = content.get('itemContent', {})
                        if item_content.get('itemType') == 'TimelineTweet':
                            tweet_results = item_content.get('tweet_results', {})
                            tweet = tweet_results.get('result', {})
                            if tweet:
                                tweets.append(tweet)
                    
                    # Handle module entries (user modules, etc.)
                    elif content.get('entryType') == 'TimelineTimelineModule':
                        items = content.get('items', [])
                        for item in items:
                            item_content = item.get('item', {}).get('itemContent', {})
                            if item_content.get('itemType') == 'TimelineTweet':
                                tweet_results = item_content.get('tweet_results', {})
                                tweet = tweet_results.get('result', {})
                                if tweet:
                                    tweets.append(tweet)
                            # elif item_content.get('itemType') == 'TimelineUser':
                            #     # Extract user data for user-focused analytics
                            #     user_results = item_content.get('user_results', {})
                            #     user = user_results.get('result', {})
                            #     if user:
                            #         # Create a pseudo-tweet for user data
                            #         user_doc = create_user_document(user)
                            #         if user_doc:
                            #             tweets.append(user_doc)
    except Exception as e:
        print(f"Error extracting tweets: {e}")
    
    return tweets


def create_tweet_document(tweet: Dict[str, Any]) -> Dict[str, Any]:
    """Create Elasticsearch document from tweet data."""
    try:
        # Extract core tweet data
        legacy = tweet.get('legacy', {})
        core = tweet.get('core', {})
        user_results = core.get('user_results', {})
        user = user_results.get('result', {})
        user_legacy = user.get('legacy', {})
        cores = user.get('core', {})
        
        # Extract text content
        full_text = legacy.get('full_text', '')
        
        # Handle note tweets (long-form content)
        note_tweet = tweet.get('note_tweet', {})
        if note_tweet.get('is_expandable'):
            note_results = note_tweet.get('note_tweet_results', {})
            note_result = note_results.get('result', {})
            if note_result.get('text'):
                full_text = note_result.get('text')
        
        # Parse created_at timestamp
        created_at = legacy.get('created_at', '')
        timestamp = parse_twitter_timestamp(created_at)
        
        # Extract engagement metrics
        metrics = {
            'like_count': legacy.get('favorite_count', 0),
            'retweet_count': legacy.get('retweet_count', 0),
            'reply_count': legacy.get('reply_count', 0),
            'quote_count': legacy.get('quote_count', 0),
            'bookmark_count': legacy.get('bookmark_count', 0),
            'view_count': tweet.get('views', {}).get('count', 0)
        }
        
        # Extract user information
        user_info = {
            'id': user.get('rest_id', ''),
            'username': cores.get('screen_name', '') or user_legacy.get('screen_name', ''),
            'display_name': cores.get('name', '') or user_legacy.get('name', ''),
            'followers_count': user_legacy.get('followers_count', 0),
            'friends_count': user_legacy.get('friends_count', 0),
            'verified': user.get('verification', {}).get('verified', False),
            'profile_image_url': user.get('avatar', {}).get('image_url', ''),
            'description': user_legacy.get('description', ''),
            'location': user.get('location', {}).get('location', '')
        }
        
        # Extract hashtags and mentions
        entities = legacy.get('entities', {})
        hashtags = [tag['text'] for tag in entities.get('hashtags', [])]
        mentions = [mention['screen_name'] for mention in entities.get('user_mentions', [])]
        urls = [url['expanded_url'] for url in entities.get('urls', [])]
        
        # Extract media information
        media = []
        extended_entities = legacy.get('extended_entities', {})
        if extended_entities.get('media'):
            for m in extended_entities['media']:
                media.append({
                    'type': m.get('type', ''),
                    'url': m.get('media_url_https', ''),
                    'id': m.get('id_str', '')
                })
        
        # Determine sentiment (placeholder - would be enhanced with ML)
        sentiment = analyze_sentiment(full_text)
        
        # Build the document
        document = {
                'platform': 'twitter',
                'platform_id': tweet.get('rest_id', ''),
                'content': full_text,
                'author': user_info,
                'timestamp': timestamp,
                'created_at': created_at,
                'metrics': metrics,
                'hashtags': hashtags,
                'mentions': mentions,
                'urls': urls,
                'media': media,
                'language': legacy.get('lang', ''),
                'sentiment': sentiment,
                'emotions': detect_emotions(full_text),
                'is_retweet': legacy.get('retweeted', False),
                'is_quote': legacy.get('is_quote_status', False),
                'conversation_id': legacy.get('conversation_id_str', ''),
                'source': "twitter",
                'possibly_sensitive': legacy.get('possibly_sensitive', False),
                'geo': extract_geo_data(tweet),
                'analyzed_at': datetime.now().isoformat(),
                'raw_data': tweet  # Keep original for debugging
            }
        if not tweet.get('rest_id', ''):
            return None
        
        return document
        
    except Exception as e:
        print(f"Error creating tweet document: {e}")
        return None


def create_user_document(user: Dict[str, Any]) -> Dict[str, Any]:
    """Create a document for user data from Twitter."""
    try:
        legacy = user.get('legacy', {})
        core = user.get('core', {})
        user_results = core.get('user_results', {}).get('core', {})
        # print(core)
        # exit()
        document = {
            '_index': 'social_media_users',
            '_id': f"twitter_user_{user.get('rest_id', '')}",
            '_score': 1.0,
            '_source': {
                'platform': 'twitter',
                'platform_id': user.get('rest_id', ''),
                'content': f"User profile: {legacy.get('name', '')} (@{legacy.get('screen_name', '')})",
                'author': {
                    'id': user.get('rest_id', ''),
                    'username': core.get('screen_name') if 'screen_name' in core else user_results.get('screen_name', ''),
                    'display_name':  core.get('name') if 'name' in core else user_results.get('name', ''),
                    'followers_count': legacy.get('followers_count', 0),
                    'friends_count': legacy.get('friends_count', 0),
                    'verified': user.get('verification', {}).get('verified', False),
                    'profile_image_url': user.get('avatar', {}).get('image_url', ''),
                    'description': legacy.get('description', ''),
                    'location': user.get('location', {}).get('location', ''),
                    'created_at': core.get('created_at', ''),
                    'statuses_count': legacy.get('statuses_count', 0),
                    'listed_count': legacy.get('listed_count', 0)
                },
                'timestamp': datetime.now().isoformat(),
                'metrics': {
                    'followers_count': legacy.get('followers_count', 0),
                    'friends_count': legacy.get('friends_count', 0),
                    'statuses_count': legacy.get('statuses_count', 0),
                    'favourites_count': legacy.get('favourites_count', 0),
                    'listed_count': legacy.get('listed_count', 0),
                    'media_count': legacy.get('media_count', 0)
                },
                'sentiment': 'neutral',
                'emotions': [],
                'analyzed_at': datetime.now().isoformat(),
                'raw_data': user
            }
        }
        print(document)
        exit()
        
        return document
        
    except Exception as e:
        print(f"Error creating user document: {e}")
        return None


def parse_twitter_timestamp(timestamp_str: str) -> str:
    """Parse Twitter timestamp to ISO format."""
    try:
        # Twitter format: "Wed Oct 05 19:55:34 +0000 2022"
        dt = datetime.strptime(timestamp_str, "%a %b %d %H:%M:%S %z %Y")
        return dt.isoformat()
    except:
        return datetime.now().isoformat()


def analyze_sentiment(text: str) -> str:
    """Basic sentiment analysis - would be enhanced with ML models."""
    # Placeholder sentiment analysis
    positive_words = ['good', 'great', 'awesome', 'amazing', 'excellent', 'happy', 'love']
    negative_words = ['bad', 'terrible', 'awful', 'hate', 'angry', 'sad', 'disappointed']
    
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
    """Basic emotion detection - would be enhanced with ML models."""
    emotions = []
    text_lower = text.lower()
    
    emotion_keywords = {
        'joy': ['happy', 'joy', 'excited', 'amazing', 'wonderful'],
        'anger': ['angry', 'mad', 'furious', 'annoyed', 'hate'],
        'sadness': ['sad', 'depressed', 'crying', 'disappointed'],
        'fear': ['scared', 'afraid', 'worried', 'anxious'],
        'surprise': ['wow', 'amazing', 'surprised', 'unbelievable'],
        'love': ['love', 'heart', 'adore', 'crush']
    }
    
    for emotion, keywords in emotion_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            emotions.append(emotion)
    
    return emotions


def extract_geo_data(tweet: Dict[str, Any]) -> Dict[str, Any]:
    """Extract geographical data from tweet."""
    geo_data = {}
    
    # Check for coordinates
    coordinates = tweet.get('coordinates')
    if coordinates:
        geo_data['coordinates'] = coordinates
    
    # Check for place data
    place = tweet.get('place')
    if place:
        geo_data['place'] = {
            'name': place.get('full_name', ''),
            'country': place.get('country', ''),
            'type': place.get('place_type', '')
        }
    
    return geo_data


def main():
    """Example usage of the parser."""
    # Load example data
    with open('/Volumes/External/Sentimind/socmed-api/example_results/twitter.json', 'r') as f:
        data = json.load(f)
    
    # Parse the data
    documents = parse_twitter_json(data)
    
    print(f"Parsed {len(documents)} documents from Twitter data")
    
    # Save parsed data
    with open('/Volumes/External/Sentimind/socmed-api/parsed_results/twitter_parsed.json', 'w') as f:
        json.dump(documents[:5], f, indent=2, ensure_ascii=False)  # Save first 5 for preview
    
    print("Sample documents saved to twitter_parsed.json")


if __name__ == "__main__":
    main()