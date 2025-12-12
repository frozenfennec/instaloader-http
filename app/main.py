from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import instaloader
import logging
import os

target_directory = os.getenv("DOWNLOAD_DIR", "/app/downloads")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Instaloader REST API", version="1.0.0")

# Singleton instance of Instaloader
# We initialize it once to handle session pooling if needed in the future
L = instaloader.Instaloader(
    sanitize_paths=True, 
    download_video_thumbnails=False,
)

class DownloadPostRequest(BaseModel):
    post_id: str
    target_directory: str | None = None

class DownloadResponse(BaseModel):
    status: str
    message: str
    post_id: str

@app.post("/api/v1/download/post", response_model=DownloadResponse)
def download_post(request: DownloadPostRequest):
    """
    Download a post by its shortcode.
    
    - **post_id**: The shortcode of the Instagram post (e.g., 'B_C-dGqF-s')
    - **target_directory**: Optional subdirectory within the downloads volume.
    """
    shortcode = request.post_id
    name = request.target_directory

    try:
        # Load the post metadata
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        logger.info(f"Post {shortcode} loaded successfully: {post}")
        # Download the post
        # Instaloader uses target_dir as the output folder name
        path = os.path.join(target_directory, name)
        downloaded = L.download_post(post, target=path)
        
        if downloaded:
            msg = f"Successfully downloaded post {shortcode} to {path}"
        else:
            msg = f"Post {shortcode} already exists in {path}"

        return DownloadResponse(
            status="success",
            message=msg,
            post_id=shortcode
        )

    except instaloader.BadResponseException as e:
        logger.error(f"Bad Response for {shortcode}: {e}")
        raise HTTPException(status_code=400, detail=f"Instagram returned a bad response: {e}")
    except instaloader.ProfileNotExistsException as e:
        logger.error(f"Profile not found for {shortcode}: {e}")
        raise HTTPException(status_code=404, detail="Profile or post not found")
    except instaloader.QueryReturnedNotFoundException as e:
        logger.error(f"Post {shortcode} not found: {e}")
        raise HTTPException(status_code=404, detail="Post not found")
    except instaloader.ConnectionException as e:
         logger.error(f"Connection error downloading {shortcode}: {e}")
         raise HTTPException(status_code=503, detail="Connection to Instagram failed")
    except Exception as e:
        logger.exception(f"Unexpected error downloading {shortcode}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "ok"}
