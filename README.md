# Instaloader REST API

A minimalistic REST API wrapper for [Instaloader](https://instaloader.github.io/), built with [FastAPI](https://fastapi.tiangolo.com/).

This project allows you to download Instagram posts via simple HTTP requests.

## Project Structure

- `app/main.py`: The API application code.
- `Dockerfile`: Configuration for building the Docker image.
- `docker-compose.yml`: Configuration for running the service with a volume for downloads.
- `requirements.txt`: Python dependencies.

## Prerequisites

- [Docker](https://www.docker.com/) and [Docker Compose](https://docs.docker.com/compose/) installed on your machine.

## Getting Started

### 1. Build and Run

To start the API and the download volume:

```bash
docker-compose up -d --build
```

The API will be accessible at: `http://localhost:8000`

### 2. API Documentation

Interactive Swagger UI documentation is available at:
`http://localhost:8000/docs`

## Usage

### Download a Post

Use the `/api/v1/download/post` endpoint to download a post by its shortcode.

**Endpoint:** `POST /api/v1/download/post`

**Parameters:**
- `post_id`: The shortcode of the post (e.g., `B_C-dGqF-s` from `instagram.com/p/B_C-dGqF-s/`).
- `target_directory`: (Optional) A subdirectory name to create within the downloads folder.
  - If omitted, files are saved directly to the volume root (`./data/instaloader_downloads`).
  - If provided (e.g., `my-folder`), files are saved to `./data/instaloader_downloads/my-folder`.

**Example Request (cURL):**

```bash
curl -X POST "http://localhost:8000/api/v1/download/post" \
     -H "Content-Type: application/json" \
     -d '{
           "post_id": "CSmC2A_sKk1", 
           "target_directory": "downloads"
         }'
```

**Response Success:**

```json
{
  "status": "success",
  "message": "Successfully downloaded post CSmC2A_sKk1 to downloads",
  "post_id": "CSmC2A_sKk1"
}
```

## Volume Mapping

The `docker-compose.yml` mounts the host directory `./data/instaloader_downloads` to `/app/downloads` in the container.
- If you request `target_directory": "downloads"`, files will populate in `./data/instaloader_downloads` on your host machine.
- If you specify a different subdirectory (e.g., `downloads/mypost`), it will create that structure inside the volume.
