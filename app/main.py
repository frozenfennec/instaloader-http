from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import instaloader
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Instaloader REST API", version="1.0.0")

# Singleton instance of Instaloader
# We initialize it once to handle session pooling if needed in the future
L = instaloader.Instaloader()

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
    
    # Constrain downloads to the 'downloads' directory (mapped volume)
    base_dir = "/app/downloads"
    if request.target_directory:
        # Create path relative to the base downloads directory
        target_dir = os.path.join(base_dir, request.target_directory)
    else:
        target_dir = base_dir

    logger.info(f"Received download request for post {shortcode} to {target_dir}")

    try:
        # Load the post metadata
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        
        # Download the post
        # Instaloader uses target_dir as the output folder name
        downloaded = L.download_post(post, target=target_dir)
        
        if downloaded:
            msg = f"Successfully downloaded post {shortcode} to {target_dir}"
        else:
            msg = f"Post {shortcode} already exists in {target_dir}"

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
