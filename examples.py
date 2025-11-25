"""
Example usage of Social Media Parsers
Demonstrates how to use individual parsers and the universal parser
"""

import json
from parsers import (
    parse_twitter_json,
    parse_instagram_json, 
    parse_tiktok_json,
    parse_facebook_json,
    parse_youtube_json
)
from parse_all import SocialMediaParser


def example_individual_parsers():
    """Example using individual platform parsers"""
    print("=== INDIVIDUAL PARSERS EXAMPLE ===\\n")
    
    # Twitter example
    print("1. Twitter Parser:")
    try:
        with open('example_results/twitter.json', 'r', encoding='utf-8') as f:
            twitter_data = json.load(f)
        
        twitter_docs = parse_twitter_json(twitter_data)
        print(f"   ✓ Parsed {len(twitter_docs)} Twitter documents")
        
        # Show first document structure
        if twitter_docs:
            first_doc = twitter_docs[0]
            print(f"   - First document ID: {first_doc['_id']}")
            print(f"   - Content preview: {first_doc['_source']['content'][:100]}...")
            print(f"   - Author: {first_doc['_source']['author']['display_name']}")
            print(f"   - Sentiment: {first_doc['_source']['sentiment']}")
    
    except Exception as e:
        print(f"   ✗ Error parsing Twitter: {e}")
    
    print()
    
    # Instagram example  
    print("2. Instagram Parser:")
    try:
        with open('example_results/instagram.json', 'r', encoding='utf-8') as f:
            instagram_data = json.load(f)
        
        instagram_docs = parse_instagram_json(instagram_data)
        print(f"   ✓ Parsed {len(instagram_docs)} Instagram documents")
        
        if instagram_docs:
            first_doc = instagram_docs[0]
            print(f"   - First document ID: {first_doc['_id']}")
            print(f"   - Media type: {first_doc['_source']['media_type']}")
            print(f"   - Hashtags: {first_doc['_source']['hashtags'][:3]}")
            print(f"   - Engagement: {first_doc['_source']['metrics']['like_count']} likes")
    
    except Exception as e:
        print(f"   ✗ Error parsing Instagram: {e}")


def example_universal_parser():
    """Example using universal parser"""
    print("\\n=== UNIVERSAL PARSER EXAMPLE ===\\n")
    
    parser = SocialMediaParser()
    
    # Parse specific file
    print("1. Parse specific file:")
    try:
        documents = parser.parse_file('example_results/tiktok.json', 'tiktok')
        print(f"   ✓ Parsed {len(documents)} TikTok documents")
        
        if documents:
            # Show analytics
            total_views = sum(doc['_source']['metrics']['view_count'] for doc in documents)
            total_likes = sum(doc['_source']['metrics']['like_count'] for doc in documents)
            print(f"   - Total views: {total_views:,}")
            print(f"   - Total likes: {total_likes:,}")
            print(f"   - Avg engagement rate: {sum(doc['_source'].get('engagement_rate', 0) for doc in documents) / len(documents):.2f}%")
    
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print()
    
    # Parse all examples
    print("2. Parse all example files:")
    try:
        results = parser.parse_all_examples('example_results')
        
        print(f"   ✓ Processed {len(results)} platforms")
        for platform, docs in results.items():
            if docs:
                print(f"   - {platform.capitalize()}: {len(docs)} documents")
        
        # Generate summary
        summary = parser.generate_summary_report(results)
        print(f"   - Total documents: {summary['total_documents']}")
        print(f"   - Most active platform: {summary['summary']['most_active_platform']}")
        print(f"   - Total engagement: {summary['summary']['total_engagement']:,}")
    
    except Exception as e:
        print(f"   ✗ Error: {e}")


def example_content_analysis():
    """Example analyzing parsed content"""
    print("\\n=== CONTENT ANALYSIS EXAMPLE ===\\n")
    
    parser = SocialMediaParser()
    results = parser.parse_all_examples('example_results')
    
    # Sentiment analysis across platforms
    print("1. Sentiment Analysis:")
    sentiment_stats = {}
    
    for platform, documents in results.items():
        if documents:
            sentiments = {'positive': 0, 'negative': 0, 'neutral': 0}
            for doc in documents:
                sentiment = doc['_source'].get('sentiment', 'neutral')
                sentiments[sentiment] += 1
            sentiment_stats[platform] = sentiments
    
    for platform, sentiments in sentiment_stats.items():
        total = sum(sentiments.values())
        if total > 0:
            print(f"   {platform.capitalize()}:")
            for sentiment, count in sentiments.items():
                percentage = (count / total) * 100
                print(f"     - {sentiment.capitalize()}: {count} ({percentage:.1f}%)")
    
    print()
    
    # Hashtag analysis
    print("2. Popular Hashtags:")
    all_hashtags = {}
    
    for platform, documents in results.items():
        if documents:
            platform_hashtags = {}
            for doc in documents:
                hashtags = doc['_source'].get('hashtags', [])
                for hashtag in hashtags:
                    hashtag_lower = hashtag.lower()
                    platform_hashtags[hashtag_lower] = platform_hashtags.get(hashtag_lower, 0) + 1
                    all_hashtags[hashtag_lower] = all_hashtags.get(hashtag_lower, 0) + 1
            
            # Show top 3 hashtags per platform
            if platform_hashtags:
                top_hashtags = sorted(platform_hashtags.items(), key=lambda x: x[1], reverse=True)[:3]
                print(f"   {platform.capitalize()}: {', '.join([f'#{tag}({count})' for tag, count in top_hashtags])}")
    
    # Overall top hashtags
    top_overall = sorted(all_hashtags.items(), key=lambda x: x[1], reverse=True)[:5]
    print(f"   Overall Top 5: {', '.join([f'#{tag}({count})' for tag, count in top_overall])}")
    
    print()
    
    # Language distribution
    print("3. Language Distribution:")
    language_stats = {}
    
    for platform, documents in results.items():
        if documents:
            languages = {}
            for doc in documents:
                lang = doc['_source'].get('language', 'unknown')
                languages[lang] = languages.get(lang, 0) + 1
            language_stats[platform] = languages
    
    all_languages = {}
    for platform, languages in language_stats.items():
        for lang, count in languages.items():
            all_languages[lang] = all_languages.get(lang, 0) + count
    
    total_docs = sum(all_languages.values())
    for lang, count in sorted(all_languages.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_docs) * 100
        lang_name = {'id': 'Indonesian', 'en': 'English', 'mixed': 'Mixed'}.get(lang, lang.capitalize())
        print(f"   {lang_name}: {count} documents ({percentage:.1f}%)")


def example_elasticsearch_format():
    """Example showing Elasticsearch-ready format"""
    print("\\n=== ELASTICSEARCH FORMAT EXAMPLE ===\\n")
    
    parser = SocialMediaParser()
    documents = parser.parse_file('example_results/youtube.json', 'youtube')
    
    if documents:
        # Show first document in Elasticsearch bulk format
        print("1. Elasticsearch Bulk API Format:")
        first_doc = documents[0]
        
        # Bulk API action
        action = {
            "index": {
                "_index": first_doc["_index"],
                "_id": first_doc["_id"]
            }
        }
        
        print("   Action:")
        print(f"   {json.dumps(action, indent=4)}")
        print()
        print("   Document:")
        print(f"   {json.dumps(first_doc['_source'], indent=4, ensure_ascii=False)[:500]}...")
        
        print()
        
        # Show index mapping suggestion
        print("2. Suggested Index Mapping:")
        mapping = {
            "mappings": {
                "properties": {
                    "platform": {"type": "keyword"},
                    "platform_id": {"type": "keyword"},
                    "content": {"type": "text", "analyzer": "standard"},
                    "timestamp": {"type": "date"},
                    "sentiment": {"type": "keyword"},
                    "language": {"type": "keyword"},
                    "hashtags": {"type": "keyword"},
                    "mentions": {"type": "keyword"},
                    "author.username": {"type": "keyword"},
                    "author.verified": {"type": "boolean"},
                    "metrics.view_count": {"type": "long"},
                    "metrics.like_count": {"type": "long"},
                    "metrics.comment_count": {"type": "long"}
                }
            }
        }
        
        print(json.dumps(mapping, indent=2))


def main():
    """Run all examples"""
    print("🚀 SOCIAL MEDIA PARSERS - USAGE EXAMPLES")
    print("=" * 50)
    
    try:
        example_individual_parsers()
        example_universal_parser()
        example_content_analysis()
        example_elasticsearch_format()
        
        print("\\n" + "=" * 50)
        print("✅ All examples completed successfully!")
        print("\\n📁 Check 'parsed_results/' directory for output files")
        print("📖 See PARSER_DOCUMENTATION.md for detailed documentation")
        
    except Exception as e:
        print(f"\\n❌ Error running examples: {e}")


if __name__ == "__main__":
    main()