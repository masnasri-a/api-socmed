# Social Media API v2.0

API komprehensif untuk mengakses berbagai platform social media menggunakan FastAPI dan RapidAPI.

## ✨ Features

- **🔥 FastAPI Framework**: Framework modern dengan performa tinggi
- **📘 Facebook**: User profiles dan page information
- **📸 Instagram**: User information
- **🐦 Twitter**: Trending topics
- **🎥 YouTube**: Video details
- **🎵 TikTok**: User profiles dan trending content
- **📚 Auto Documentation**: Swagger UI dan ReDoc
- **🚀 Async Operations**: Semua operasi bersifat asynchronous
- **🔒 Security**: Optional Bearer token authentication
- **🌐 CORS Support**: CORS middleware untuk cross-origin requests
- **⚡ Error Handling**: Comprehensive error handling
- **🔧 Environment Config**: Environment variables support

## 📁 Project Structure

```
socmed-api/
├── main.py              # FastAPI application utama
├── run_server.py        # Server launcher script
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables
├── README.md           # Documentation
├── test_api.py         # Testing script
└── services/           # Service modules
    ├── __init__.py     # Package initializer
    ├── facebook.py     # Facebook service
    ├── instagram.py    # Instagram service
    ├── twitter.py      # Twitter service
    └── youtube.py      # YouTube service
```

## 🛠️ Installation

1. **Clone atau download project**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment** (optional):
   Edit file `.env` untuk mengubah konfigurasi

4. **Run the server**:
   ```bash
   python run_server.py
   ```
   
   Atau menggunakan uvicorn langsung:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

## 🌐 API Endpoints

### Health & Info
- `GET /` - Root endpoint dengan informasi API
- `GET /health` - Health check endpoint

### Facebook
- `POST /facebook/user` - Get Facebook user profile (JSON body)
- `POST /facebook/page` - Get Facebook page info (JSON body)
- `GET /facebook/user/{username}` - Get Facebook user profile (URL param)
- `GET /facebook/page/{page_id}` - Get Facebook page info (URL param)

### Instagram  
- `POST /instagram/user` - Get user info (JSON body)
- `GET /instagram/user/{username}` - Get user info (URL param)

### Twitter
- `POST /twitter/trending` - Get trending topics (JSON body)
- `GET /twitter/trending` - Get trending topics (URL param)

### YouTube
- `POST /youtube/video` - Get video details (JSON body)
- `GET /youtube/video/{video_id}` - Get video details (URL param)

### TikTok
- `POST /tiktok/user` - Get user profile (JSON body)
- `GET /tiktok/user/{username}` - Get user profile (URL param)
- `GET /tiktok/trending` - Get trending content
- `POST /youtube/search` - Search videos (JSON body)
- `POST /youtube/video` - Get video details (JSON body)
- `GET /youtube/search/{query}` - Search videos (URL param)
- `GET /youtube/video/{video_id}` - Get video details (URL param)

## 📖 API Documentation

Setelah server berjalan, akses dokumentasi interaktif di:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🧪 Usage Examples

### Using cURL

1. **Facebook Search**:
   ```bash
   curl -X POST "http://localhost:8000/facebook/search" \
     -H "Content-Type: application/json" \
     -d '{"query": "programming"}'
   ```

2. **Instagram Search**:
   ```bash
   curl -X POST "http://localhost:8000/instagram/search" \
     -H "Content-Type: application/json" \
     -d '{"query": "travel"}'
   ```

3. **Instagram User Info**:
   ```bash
   curl -X POST "http://localhost:8000/instagram/user" \
     -H "Content-Type: application/json" \
     -d '{"username": "instagram"}'
   ```

4. **Twitter Search**:
   ```bash
   curl -X POST "http://localhost:8000/twitter/search" \
     -H "Content-Type: application/json" \
     -d '{"query": "technology", "type": "Top", "count": 10}'
   ```

5. **Twitter Trending**:
   ```bash
   curl -X POST "http://localhost:8000/twitter/trending" \
     -H "Content-Type: application/json" \
     -d '{"woeid": 1}'
   ```

6. **YouTube Search**:
   ```bash
   curl -X POST "http://localhost:8000/youtube/search" \
     -H "Content-Type: application/json" \
     -d '{"query": "python tutorial", "hl": "en", "gl": "US"}'
   ```

6. **TikTok Search**:
   ```bash
   curl -X POST "http://localhost:8000/tiktok/search/general" \
     -H "Content-Type: application/json" \
     -d '{"keyword": "dance", "cursor": "0", "search_id": "0"}'
   ```

### Using GET Requests

- **Facebook**: `http://localhost:8000/facebook/search/programming`
- **Instagram**: `http://localhost:8000/instagram/search/travel`  
- **Instagram User**: `http://localhost:8000/instagram/user/instagram`
- **Twitter**: `http://localhost:8000/twitter/search/technology?search_type=Top&count=10`
- **Twitter Trending**: `http://localhost:8000/twitter/trending?woeid=1`
- **YouTube**: `http://localhost:8000/youtube/search/python%20tutorial?hl=en&gl=US`
- **TikTok**: `http://localhost:8000/tiktok/search/general/dance?cursor=0&search_id=0`

## 📝 Response Format

Semua endpoint mengembalikan response dalam format JSON yang konsisten:

### Success Response:
```json
{
  "status": "success",
  "message": "Operation completed successfully",
  "data": {
    // API response data dari platform terkait
  }
}
```

### Error Response:
```json
{
  "status": "error",
  "message": "Error description",
  "error": "Detailed error message",
  "data": null
}
```

## 🔧 Configuration

### Environment Variables (.env)
```env
RAPIDAPI_KEY=your_rapidapi_key_here
HOST=0.0.0.0
PORT=8000
RELOAD=true
API_TITLE="Social Media API"
API_VERSION="2.0.0"
```

### Dependencies (requirements.txt)
- FastAPI 0.104.1
- Uvicorn 0.24.0
- Pydantic 2.5.0
- Requests 2.31.0
- Python-multipart 0.0.6
- Python-dotenv 1.0.0

## 🧪 Testing

Jalankan script testing untuk memverifikasi semua endpoint:
```bash
python test_api.py
```

## 🔑 Authentication

API mendukung optional Bearer token authentication. Untuk menggunakan:

```bash
curl -X POST "http://localhost:8000/instagram/search" \
  -H "Authorization: Bearer your_token_here" \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}'
```

## ⚙️ Development

### Requirements
- Python 3.7+
- FastAPI
- Uvicorn
- RapidAPI Account

### Features
- Hot reload dalam development mode
- Comprehensive error handling
- Input validation dengan Pydantic
- Type hints di semua functions
- Async/await pattern untuk performa optimal
- CORS support untuk frontend integration

## 🚀 Deployment

### Local Development
```bash
python run_server.py
```

### Production
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker (Optional)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📞 Support

Jika mengalami masalah atau butuh bantuan:
1. Check dokumentasi API di `/docs`
2. Pastikan semua dependencies terinstall
3. Verify RapidAPI key validity
4. Check server logs untuk error details

## 🔄 API Versions

- **v1.0**: Basic functionality
- **v2.0**: Enhanced features, better error handling, comprehensive documentation

---

**Happy Coding! 🚀**