"""
Universal Social Media Parser
Converts various social media platform JSON responses to standardized Elasticsearch format
for social media monitoring analytics.
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import all platform parsers
from parsers.twitter_parser import parse_twitter_json
from parsers.instagram_parser import parse_instagram_json
from parsers.tiktok_parser import parse_tiktok_json
from parsers.facebook_parser import parse_facebook_json
from parsers.youtube_parser import parse_youtube_json


class SocialMediaParser:
    """Universal parser for social media platform data."""
    
    def __init__(self):
        self.parsers = {
            'twitter': parse_twitter_json,
            'instagram': parse_instagram_json,
            'tiktok': parse_tiktok_json,
            'facebook': parse_facebook_json,
            'youtube': parse_youtube_json
        }
    
    def parse_platform_data(self, platform: str, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse data from a specific social media platform.
        
        Args:
            platform: Platform name ('twitter', 'instagram', 'tiktok', 'facebook', 'youtube')
            data: Raw JSON data from platform API
            
        Returns:
            List of documents in Elasticsearch format
        """
        if platform not in self.parsers:
            raise ValueError(f"Unsupported platform: {platform}. Supported: {list(self.parsers.keys())}")
        
        parser_func = self.parsers[platform]
        return parser_func(data)
    
    def parse_file(self, file_path: str, platform: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Parse a JSON file from a social media platform.
        
        Args:
            file_path: Path to the JSON file
            platform: Platform name (if None, will try to detect from filename)
            
        Returns:
            List of documents in Elasticsearch format
        """
        # Auto-detect platform if not specified
        if platform is None:
            filename = os.path.basename(file_path).lower()
            for platform_name in self.parsers.keys():
                if platform_name in filename:
                    platform = platform_name
                    break
            
            if platform is None:
                raise ValueError(f"Could not detect platform from filename: {filename}")
        
        # Load and parse the file
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return self.parse_platform_data(platform, data)
    
    def parse_all_examples(self, examples_dir: str = 'example_results') -> Dict[str, List[Dict[str, Any]]]:
        """
        Parse all example files in the examples directory.
        
        Args:
            examples_dir: Directory containing example JSON files
            
        Returns:
            Dictionary with platform as key and parsed documents as values
        """
        results = {}
        
        example_files = {
            'twitter': 'twitter.json',
            'instagram': 'instagram.json',
            'tiktok': 'tiktok.json',
            'facebook': 'facebook.json',
            'youtube': 'youtube.json'
        }
        
        for platform, filename in example_files.items():
            file_path = os.path.join(examples_dir, filename)
            
            if os.path.exists(file_path):
                try:
                    print(f"Parsing {platform} data from {file_path}...")
                    documents = self.parse_file(file_path, platform)
                    results[platform] = documents
                    print(f"✓ Parsed {len(documents)} documents from {platform}")
                except Exception as e:
                    print(f"✗ Error parsing {platform}: {e}")
                    results[platform] = []
            else:
                print(f"⚠ File not found: {file_path}")
                results[platform] = []
        
        return results
    
    def save_parsed_results(self, results: Dict[str, List[Dict[str, Any]]], output_dir: str = 'parsed_results'):
        """
        Save parsed results to files.
        
        Args:
            results: Dictionary with platform as key and parsed documents as values
            output_dir: Directory to save parsed results
        """
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        for platform, documents in results.items():
            if documents:
                output_file = os.path.join(output_dir, f'{platform}_parsed.json')
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(documents, f, indent=2, ensure_ascii=False)
                
                print(f"Saved {len(documents)} {platform} documents to {output_file}")
    
    def generate_summary_report(self, results: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """
        Generate a summary report of parsed data.
        
        Args:
            results: Dictionary with platform as key and parsed documents as values
            
        Returns:
            Summary report dictionary
        """
        total_documents = sum(len(docs) for docs in results.values())
        
        platform_stats = {}
        for platform, documents in results.items():
            if documents:
                # Count sentiments
                sentiments = {'positive': 0, 'negative': 0, 'neutral': 0}
                languages = {}
                total_engagement = 0
                
                for doc in documents:
                    source = doc.get('_source', {})
                    
                    # Count sentiment
                    sentiment = source.get('sentiment', 'neutral')
                    sentiments[sentiment] = sentiments.get(sentiment, 0) + 1
                    
                    # Count languages
                    lang = source.get('language', 'unknown')
                    languages[lang] = languages.get(lang, 0) + 1
                    
                    # Sum engagement metrics
                    metrics = source.get('metrics', {})
                    if platform == 'twitter':
                        total_engagement += metrics.get('like_count', 0) + metrics.get('retweet_count', 0)
                    elif platform == 'instagram':
                        total_engagement += metrics.get('like_count', 0) + metrics.get('comment_count', 0)
                    elif platform == 'tiktok':
                        total_engagement += metrics.get('like_count', 0) + metrics.get('share_count', 0)
                    elif platform == 'facebook':
                        total_engagement += metrics.get('reactions_count', 0) + metrics.get('comments_count', 0)
                    elif platform == 'youtube':
                        total_engagement += metrics.get('view_count', 0)
                
                platform_stats[platform] = {
                    'document_count': len(documents),
                    'sentiment_breakdown': sentiments,
                    'language_breakdown': languages,
                    'total_engagement': total_engagement,
                    'avg_engagement': round(total_engagement / len(documents), 2) if documents else 0
                }
            else:
                platform_stats[platform] = {
                    'document_count': 0,
                    'sentiment_breakdown': {'positive': 0, 'negative': 0, 'neutral': 0},
                    'language_breakdown': {},
                    'total_engagement': 0,
                    'avg_engagement': 0
                }
        
        return {
            'generated_at': datetime.now().isoformat(),
            'total_documents': total_documents,
            'platforms': platform_stats,
            'summary': {
                'most_active_platform': max(platform_stats.keys(), key=lambda x: platform_stats[x]['document_count']) if platform_stats else None,
                'total_engagement': sum(stats['total_engagement'] for stats in platform_stats.values()),
                'platforms_processed': len([p for p, stats in platform_stats.items() if stats['document_count'] > 0])
            }
        }


def main():
    """Main function to demonstrate the parser usage."""
    print("🚀 Starting Social Media Parser...")
    print("=" * 50)
    
    # Initialize parser
    parser = SocialMediaParser()
    
    # Parse all example files
    print("📂 Parsing example files...")
    results = parser.parse_all_examples('/Volumes/External/Sentimind/socmed-api/example_results')
    
    print("\\n" + "=" * 50)
    
    # Save parsed results
    print("💾 Saving parsed results...")
    parser.save_parsed_results(results, '/Volumes/External/Sentimind/socmed-api/parsed_results')
    
    print("\\n" + "=" * 50)
    
    # Generate summary report
    print("📊 Generating summary report...")
    summary = parser.generate_summary_report(results)
    
    # Save summary report
    with open('/Volumes/External/Sentimind/socmed-api/parsed_results/summary_report.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print(f"\\n📈 SUMMARY REPORT")
    print(f"Total documents parsed: {summary['total_documents']}")
    print(f"Platforms processed: {summary['summary']['platforms_processed']}")
    print(f"Most active platform: {summary['summary']['most_active_platform']}")
    print(f"Total engagement: {summary['summary']['total_engagement']:,}")
    
    print("\\n📋 Platform Breakdown:")
    for platform, stats in summary['platforms'].items():
        if stats['document_count'] > 0:
            print(f"  {platform.capitalize()}:")
            print(f"    Documents: {stats['document_count']}")
            print(f"    Avg Engagement: {stats['avg_engagement']:,.2f}")
            print(f"    Sentiments: {stats['sentiment_breakdown']}")
    
    print("\\n✅ Parsing completed! Check the 'parsed_results' directory for output files.")


if __name__ == "__main__":
    main()