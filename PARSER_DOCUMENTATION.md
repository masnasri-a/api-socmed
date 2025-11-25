# Social Media Parsers - Dokumentasi

Parser JSON untuk platform media sosial yang mengkonversi data API ke format Elasticsearch standar untuk analitik social media monitoring.

## 🚀 Overview

Parser ini mengkonversi data JSON mentah dari berbagai platform media sosial menjadi format dokumen Elasticsearch yang terstandarisasi untuk analisis monitoring media sosial.

### Platform yang Didukung:
- **Twitter** - Timeline, tweets, user data
- **Instagram** - Media posts, clips, user profiles  
- **TikTok** - Video content, user data, trending
- **Facebook** - Posts, reactions, media
- **YouTube** - Video search results, channel info

## 📋 Format Output Elasticsearch

Semua parser menghasilkan dokumen dengan struktur standar:

```json
{
  "_index": "social_media_posts",
  "_id": "platform_postid",
  "_score": 1.0,
  "_source": {
    "platform": "platform_name",
    "platform_id": "unique_post_id",
    "content": "text_content",
    "author": {
      "id": "user_id",
      "username": "username",
      "display_name": "display_name",
      "followers_count": 0,
      "verified": false,
      "profile_image_url": "url",
      "description": "bio"
    },
    "timestamp": "2025-01-01T00:00:00.000Z",
    "metrics": {
      "like_count": 0,
      "comment_count": 0,
      "share_count": 0,
      "view_count": 0
    },
    "hashtags": ["tag1", "tag2"],
    "mentions": ["user1", "user2"],
    "sentiment": "positive|negative|neutral",
    "emotions": ["joy", "excitement"],
    "language": "en|id|mixed",
    "analyzed_at": "2025-01-01T00:00:00.000Z",
    "raw_data": {}
  }
}
```

## 🔧 Instalasi dan Penggunaan

### 1. Instalasi Dependencies
```bash
pip install python-dateutil
```

### 2. Struktur File
```
socmed-api/
├── parsers/
│   ├── __init__.py
│   ├── twitter_parser.py
│   ├── instagram_parser.py
│   ├── tiktok_parser.py
│   ├── facebook_parser.py
│   └── youtube_parser.py
├── example_results/
│   ├── twitter.json
│   ├── instagram.json
│   ├── tiktok.json
│   ├── facebook.json
│   └── youtube.json
├── parsed_results/
└── parse_all.py
```

### 3. Penggunaan Individual Parser

#### Twitter Parser
```python
from parsers.twitter_parser import parse_twitter_json

with open('twitter.json', 'r') as f:
    data = json.load(f)

documents = parse_twitter_json(data)
```

#### Instagram Parser
```python
from parsers.instagram_parser import parse_instagram_json

with open('instagram.json', 'r') as f:
    data = json.load(f)

documents = parse_instagram_json(data)
```

### 4. Penggunaan Universal Parser

```python
from parse_all import SocialMediaParser

parser = SocialMediaParser()

# Parse single file
documents = parser.parse_file('example.json', 'twitter')

# Parse all examples
results = parser.parse_all_examples('example_results/')

# Save results
parser.save_parsed_results(results, 'output/')
```

### 5. Menjalankan Parser Batch
```bash
cd /path/to/socmed-api
python3 parse_all.py
```

## 📊 Fitur Analytics

### 1. Sentiment Analysis
- **Positive**: Kata-kata positif terdeteksi
- **Negative**: Kata-kata negatif terdeteksi  
- **Neutral**: Tidak ada indikator sentimen yang kuat

### 2. Emotion Detection
Emosi yang terdeteksi:
- `joy` - Kegembiraan
- `love` - Cinta/kasih sayang
- `anger` - Kemarahan
- `sadness` - Kesedihan
- `surprise` - Kejutan
- `fear` - Ketakutan
- `humor` - Humor/lucu
- `excitement` - Antusiasme
- `inspiration` - Inspirasi

### 3. Language Detection
- `id` - Bahasa Indonesia
- `en` - Bahasa Inggris
- `mixed` - Campuran bahasa
- `unknown` - Tidak terdeteksi

### 4. Content Categorization
Kategori konten yang terdeteksi:
- `music` - Musik
- `gaming` - Gaming
- `education` - Edukasi
- `comedy` - Komedi
- `lifestyle` - Gaya hidup
- `food` - Makanan
- `fashion` - Fashion
- `sports` - Olahraga
- `technology` - Teknologi

## 🎯 Data yang Diekstrak

### Twitter
- Timeline tweets dan user data
- Engagement metrics (likes, retweets, replies)
- Hashtags, mentions, URLs
- Media attachments
- User verification status
- Geographical data
- Note tweets (long-form content)

### Instagram
- Media posts (images, videos, clips)
- Captions dan stories
- Engagement metrics (likes, comments, views)
- Hashtags dan mentions
- Location data
- Video duration dan play counts
- User profiles dan verification

### TikTok
- Video content dan descriptions
- Engagement metrics (views, likes, shares)
- Music information
- Challenges dan effects
- User statistics
- Video technical details
- Hashtags dan trends

### Facebook  
- Post content dan rich text
- Reactions breakdown (like, love, wow, etc.)
- Comments dan shares count
- Media attachments
- External links
- Author information
- Event attachments

### YouTube
- Video metadata (title, description)
- Channel information
- View counts
- Thumbnails dan moving thumbnails
- Video duration
- Publishing timestamps
- Badges dan verification
- Content categorization

## 📈 Hasil Parsing

### Statistik Hasil Parsing:
- **Total documents**: 75
- **Twitter**: 28 documents (680 avg engagement)
- **Instagram**: 4 documents (110,756 avg engagement) 
- **TikTok**: 12 documents (28,050 avg engagement)
- **Facebook**: 2 documents (164 avg engagement)
- **YouTube**: 29 documents (35,725 avg engagement)

### Distribusi Bahasa:
- **Indonesia**: 21 documents
- **English**: 36 documents  
- **Mixed**: 5 documents
- **Unknown**: 13 documents

## 🛠 Kustomisasi

### 1. Menambah Platform Baru
```python
def parse_newplatform_json(data):
    # Implementation here
    return documents

# Tambahkan ke SocialMediaParser
parser.parsers['newplatform'] = parse_newplatform_json
```

### 2. Menambah Field Analytics
```python
# Dalam create_document function
document['_source']['custom_field'] = extract_custom_data(data)
```

### 3. Sentiment Analysis Kustom
```python
def custom_sentiment_analysis(text):
    # Custom ML model implementation
    return sentiment_score

# Replace dalam parser
sentiment = custom_sentiment_analysis(content)
```

## 🔍 Troubleshooting

### Error Umum:

1. **File tidak ditemukan**
   ```
   FileNotFoundError: [Errno 2] No such file or directory
   ```
   - Pastikan path file benar
   - Cek struktur direktori

2. **JSON parsing error**
   ```
   JSONDecodeError: Expecting value
   ```
   - Pastikan file JSON valid
   - Cek encoding file (gunakan UTF-8)

3. **Missing fields**
   ```
   KeyError: 'field_name'
   ```
   - Struktur JSON mungkin berbeda
   - Tambahkan handling untuk optional fields

### Debug Mode
Aktifkan debug dengan menambah print statements:
```python
print(f"Processing {len(items)} items...")
print(f"Document created: {document['_id']}")
```

## 📁 Output Files

Parser menghasilkan file output di direktori `parsed_results/`:

- `twitter_parsed.json` - Data Twitter yang diparsed
- `instagram_parsed.json` - Data Instagram yang diparsed  
- `tiktok_parsed.json` - Data TikTok yang diparsed
- `facebook_parsed.json` - Data Facebook yang diparsed
- `youtube_parsed.json` - Data YouTube yang diparsed
- `summary_report.json` - Laporan ringkasan analytics

## 🚀 Integrasi Elasticsearch

### 1. Bulk Upload ke Elasticsearch
```python
from elasticsearch import Elasticsearch

es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

def bulk_upload(documents):
    actions = []
    for doc in documents:
        actions.append({
            '_index': doc['_index'],
            '_id': doc['_id'],
            '_source': doc['_source']
        })
    
    es.bulk(body=actions)
```

### 2. Index Mapping
```json
{
  "mappings": {
    "properties": {
      "platform": {"type": "keyword"},
      "content": {"type": "text", "analyzer": "standard"},
      "timestamp": {"type": "date"},
      "sentiment": {"type": "keyword"},
      "hashtags": {"type": "keyword"},
      "metrics": {
        "properties": {
          "like_count": {"type": "long"},
          "view_count": {"type": "long"}
        }
      }
    }
  }
}
```

## 🎯 Use Cases

### 1. Social Media Monitoring
- Track brand mentions across platforms
- Monitor hashtag campaigns
- Analyze competitor content

### 2. Sentiment Analysis
- Brand sentiment tracking
- Crisis management
- Customer feedback analysis

### 3. Influencer Analytics
- Engagement rate analysis
- Content performance tracking
- Audience analysis

### 4. Trend Analysis
- Hashtag trend monitoring
- Viral content identification
- Cross-platform content analysis

## 📊 Analytics Dashboard Integration

Data yang diparsed dapat diintegrasikan dengan dashboard seperti:
- **Kibana** - Visualisasi Elasticsearch
- **Grafana** - Time-series analytics
- **Power BI** - Business intelligence
- **Tableau** - Advanced visualizations

## 🔐 Compliance & Privacy

- Parser tidak menyimpan data pribadi yang sensitif
- Data mentah disimpan untuk debugging (dapat dinonaktifkan)
- Mengikuti format standar untuk GDPR compliance
- Rate limiting untuk API calls (implementasi terpisah)

## 📞 Support

Untuk pertanyaan atau issues, silakan buat issue di repository atau hubungi tim development.

---

**Version**: 1.0.0  
**Last Updated**: November 2025  
**Compatibility**: Python 3.7+