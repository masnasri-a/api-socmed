from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import asyncio
import uvicorn
import os
from dotenv import load_dotenv

from services import FacebookService, InstagramService, TwitterService, YoutubeService, TikTokService
from parsers import parse_facebook_json, parse_instagram_json, parse_twitter_json, parse_youtube_json, parse_tiktok_json

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Social Media API",
    description="API komprehensif untuk mengakses berbagai platform social media",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Security
security = HTTPBearer(auto_error=False)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
API_KEY = os.getenv("RAPIDAPI_KEY")

# Request/Response Models
class UserInfoRequest(BaseModel):
    username: str = Field(..., description="Username to lookup", json_schema_extra={"example": "username"})

class VideoDetailsRequest(BaseModel):
    video_id: str = Field(..., description="YouTube video ID", json_schema_extra={"example": "dQw4w9WgXcQ"})

class TrendingRequest(BaseModel):
    woeid: int = Field(default=1, description="Where On Earth ID", json_schema_extra={"example": 1})

class PageInfoRequest(BaseModel):
    page_id: str = Field(..., description="Facebook page ID", json_schema_extra={"example": "cnn"})

class UserInfoRequest(BaseModel):
    username: str = Field(..., description="Username to lookup", json_schema_extra={"example": "username"})

class VideoDetailsRequest(BaseModel):
    video_id: str = Field(..., description="YouTube video ID", json_schema_extra={"example": "dQw4w9WgXcQ"})

class TrendingRequest(BaseModel):
    woeid: int = Field(default=1, description="Where On Earth ID", json_schema_extra={"example": 1})


class TikTokSearchRequest(BaseModel):
    keyword: str = Field(..., description="Search keyword", json_schema_extra={"example": "prabowo"})
    cursor: str = Field(default="0", description="Pagination cursor", json_schema_extra={"example": "0"})
    search_id: str = Field(default="0", description="Search session ID", json_schema_extra={"example": "0"})

class APIResponse(BaseModel):
    status: str
    message: str = None
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Initialize services
facebook_service = FacebookService(API_KEY)
instagram_service = InstagramService(API_KEY)
twitter_service = TwitterService(API_KEY)
youtube_service = YoutubeService(API_KEY)
tiktok_service = TikTokService(API_KEY)

# Dependency untuk validasi API key (optional)
async def get_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials:
        return credentials.credentials
    return None

# Root endpoints
@app.get("/")
async def root():
    """Root endpoint dengan informasi API"""
    return {
        "message": "Social Media API v2.0 with Integrated Parsers",
        "status": "running",
        "documentation": "/docs",
        "endpoints": {
            "facebook": "/facebook/search/{keyword}",
            "instagram": "/instagram/search/{keyword}",
            "twitter": "/twitter/search/{keyword}",
            "youtube": "/youtube/search/{keyword}",
            "tiktok": "/tiktok/search/{keyword}",
            "parsed_data": "/parsed/{platform}/search/{keyword}"
        },
        "features": [
            "Real-time social media data retrieval",
            "Automatic data parsing to Elasticsearch format",
            "Sentiment analysis and emotion detection",
            "Hashtag and mention extraction",
            "Cross-platform analytics support"
        ]
    }

@app.get("/health", response_model=APIResponse)
async def health_check():
    """Health check endpoint"""
    return APIResponse(
        status="success",
        message="API is healthy and running properly",
        data={"timestamp": "2025-11-20", "version": "2.0.0"}
    )

@app.get("/facebook/search/{keyword}", response_model=APIResponse, tags=["Facebook"])
async def get_facebook_page_get(keyword: str):
    """Get Facebook search results via GET"""
    try:
        result = await asyncio.get_event_loop().run_in_executor(
            None, facebook_service.search_posts, keyword
        )
        
        # Parse data menggunakan Facebook parser
        parsed_documents = parse_facebook_json(result)
        
        # Tambahkan source_socmed ke setiap dokumen
        for doc in parsed_documents:
            doc['_source']['source_socmed'] = 'facebook'
        
        return APIResponse(
            status="success",
            message="Facebook search results retrieved and parsed",
            data={
                "raw_data": result,
                "parsed_documents": parsed_documents,
                "total_documents": len(parsed_documents)
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/instagram/search/{keyword}", response_model=APIResponse, tags=["Instagram"])
async def get_instagram_user_get(keyword: str):
    """Get Instagram search results via GET"""
    try:
        result = await instagram_service.search(keyword)
        
        # Parse data menggunakan Instagram parser
        parsed_documents = parse_instagram_json(result)
        
        # Tambahkan source_socmed ke setiap dokumen
        for doc in parsed_documents:
            doc['_source']['source_socmed'] = 'instagram'
        
        return APIResponse(
            status="success",
            message="Instagram search results retrieved and parsed",
            data={
                "raw_data": result,
                "parsed_documents": parsed_documents,
                "total_documents": len(parsed_documents)
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/twitter/search/{keyword}", response_model=APIResponse, tags=["Twitter"])
async def get_twitter_trending_get(keyword: str = 1):
    """Get Twitter trending topics via GET"""
    try:
        result = await twitter_service.search(keyword)
        
        # Parse data menggunakan Twitter parser
        parsed_documents = parse_twitter_json(result)
        
        # Tambahkan source_socmed ke setiap dokumen
        for doc in parsed_documents:
            doc['_source']['source_socmed'] = 'twitter'
        
        return APIResponse(
            status="success",
            message="Twitter trending topics retrieved and parsed",
            data={
                "raw_data": result,
                "parsed_documents": parsed_documents,
                "total_documents": len(parsed_documents)
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/youtube/search/{keyword}", response_model=APIResponse, tags=["YouTube"])
async def get_youtube_video_get(keyword: str):
    """Get YouTube video details via GET"""
    try:
        result = await youtube_service.search(keyword)
        
        # Parse data menggunakan YouTube parser
        parsed_documents = parse_youtube_json(result)
        
        # Tambahkan source_socmed ke setiap dokumen
        for doc in parsed_documents:
            doc['_source']['source_socmed'] = 'youtube'
        
        return APIResponse(
            status="success",
            message="YouTube video details retrieved and parsed",
            data={
                "raw_data": result,
                "parsed_documents": parsed_documents,
                "total_documents": len(parsed_documents)
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tiktok/search/{keyword}", response_model=APIResponse, tags=["TikTok"])
async def get_tiktok_trending(keyword: str):
    """Get TikTok trending content"""
    try:
        result = await tiktok_service.search_general(keyword)
        
        # Parse data menggunakan TikTok parser
        parsed_documents = parse_tiktok_json(result)
        
        # Tambahkan source_socmed ke setiap dokumen
        for doc in parsed_documents:
            doc['_source']['source_socmed'] = 'tiktok'
        
        return APIResponse(
            status="success",
            message="TikTok trending content retrieved and parsed",
            data={
                "raw_data": result,
                "parsed_documents": parsed_documents,
                "total_documents": len(parsed_documents)
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint untuk mendapatkan data yang sudah diparsed saja
@app.get("/parsed/{platform}/search/{keyword}", response_model=APIResponse, tags=["Parsed Data"])
async def get_parsed_data(platform: str, keyword: str):
    """Get parsed social media data without raw data"""
    try:
        platform = platform.lower()
        
        if platform == "facebook":
            result = await asyncio.get_event_loop().run_in_executor(
                None, facebook_service.search_posts, keyword
            )
            parsed_documents = parse_facebook_json(result)
            source_socmed = "facebook"
            
        elif platform == "instagram":
            result = await instagram_service.search(keyword)
            parsed_documents = parse_instagram_json(result)
            source_socmed = "instagram"
            
        elif platform == "twitter":
            result = await twitter_service.search(keyword)
            parsed_documents = parse_twitter_json(result)
            source_socmed = "twitter"
            
        elif platform == "youtube":
            result = await youtube_service.search(keyword)
            parsed_documents = parse_youtube_json(result)
            source_socmed = "youtube"
            
        elif platform == "tiktok":
            result = await tiktok_service.search_general(keyword)
            parsed_documents = parse_tiktok_json(result)
            source_socmed = "tiktok"
            
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported platform: {platform}")
        
        # Tambahkan source_socmed ke setiap dokumen
        for doc in parsed_documents:
            doc['_source']['source_socmed'] = source_socmed
        
        return APIResponse(
            status="success",
            message=f"{platform.capitalize()} search results parsed successfully",
            data={
                "platform": platform,
                "source_socmed": source_socmed,
                "documents": parsed_documents,
                "total_documents": len(parsed_documents),
                "search_keyword": keyword
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=404,
        content={
            "status": "error",
            "message": "Endpoint not found",
            "error": "404 Not Found"
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=500,
        content={
            "status": "error", 
            "message": "Internal server error",
            "error": "500 Internal Server Error"
        }
    )

if __name__ == "__main__":
    print("🚀 Starting Social Media API v2.0 with Integrated Parsers...")
    print("📖 Dokumentasi tersedia di:")
    print("   - Swagger UI: http://localhost:8000/docs")
    print("   - ReDoc: http://localhost:8000/redoc")
    print("🔧 Endpoints yang tersedia:")
    print("   - Facebook: /facebook/search/{keyword}")
    print("   - Instagram: /instagram/search/{keyword}")
    print("   - Twitter: /twitter/search/{keyword}")
    print("   - YouTube: /youtube/search/{keyword}")
    print("   - TikTok: /tiktok/search/{keyword}")
    print("   - Parsed Data: /parsed/{platform}/search/{keyword}")
    print("✨ Fitur:")
    print("   - Parsing otomatis ke format Elasticsearch")
    print("   - Analisis sentimen dan emosi")
    print("   - Ekstraksi hashtag dan mention")
    print("   - Field 'source_socmed' pada setiap dokumen")
    print("💡 Tekan Ctrl+C untuk menghentikan server")
    print("=" * 60)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )
