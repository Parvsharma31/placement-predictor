# Student Placement Prediction API

Production-style REST API that predicts student placement outcomes using a scikit-learn model, with PostgreSQL persistence and Docker support.

![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688?logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4.2-F7931E?logo=scikit-learn&logoColor=white)

## Features

- **ML prediction** — Random Forest classifier trained on synthetic student data
- **CRUD API** — Create, read, update, and delete prediction records
- **Pydantic validation** — Strict request/response schemas with field constraints
- **Computed fields** — `placement_readiness_score` derived from student inputs
- **PostgreSQL storage** — Predictions persisted with SQLAlchemy ORM
- **Docker support** — Multi-container setup with `docker compose`

## Project Structure

```
placement_predictor/
├── app/
│   ├── main.py                 # FastAPI entry point
│   ├── config.py               # Environment settings
│   ├── routes/
│   │   ├── health.py           # Health check endpoint
│   │   └── prediction.py       # Prediction CRUD routes
│   ├── schemas/
│   │   ├── request_schema.py   # Pydantic request models
│   │   └── response_schema.py    # Pydantic response models
│   ├── services/
│   │   └── predictor.py        # Model loading and inference
│   └── database/
│       ├── connection.py       # SQLAlchemy engine and session
│       └── models.py           # ORM models
├── ml/
│   ├── train_model.py          # Model training script
│   └── model.pkl               # Trained pipeline (generated)
├── .env                        # Local environment variables
├── .env.example                # Environment template
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## Local Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd placement_predictor
```

### 2. Create a virtual environment

```bash
python -m venv .venv

# Windows
.\.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

> **Note:** Python 3.11 is recommended. Some pinned dependencies may not install on Python 3.13+.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and set your values (see [Environment Variables](#environment-variables) below).

Example:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/placement_db
MODEL_PATH=ml/model.pkl
MODEL_VERSION=1.0.0
DEBUG=True
```

### 5. Train the model

```bash
python ml/train_model.py
```

This generates `ml/model.pkl` and prints a classification report on the test set.

### 6. Run the API

```bash
uvicorn app.main:app --reload
```

The API will be available at **http://127.0.0.1:8000**. Interactive docs: **http://127.0.0.1:8000/docs**

## Docker Setup

Ensure Docker Desktop is running, then:

```bash
python ml/train_model.py   # generate model.pkl before first run
docker compose up --build
```

This starts:

- **db** — PostgreSQL 15 on port `5432`
- **api** — FastAPI app on port `8000`, with `./ml` mounted for model persistence

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health/` | Health check — reports API status, model version, and database connectivity |
| `POST` | `/predictions/predict` | Run ML prediction and save result to the database |
| `GET` | `/predictions/` | List all predictions (supports filtering and sorting) |
| `GET` | `/predictions/{prediction_id}` | Retrieve a single prediction by ID |
| `PUT` | `/predictions/{prediction_id}` | Partially update a prediction record |
| `DELETE` | `/predictions/{prediction_id}` | Delete a prediction record |

### Example Requests

**Create a prediction:**

```bash
curl -X POST http://127.0.0.1:8000/predictions/predict \
  -H "Content-Type: application/json" \
  -d '{
    "academic": {
      "cgpa": 8.5,
      "aptitude_score": 78
    },
    "skills": {
      "communication_score": 82,
      "dsa_score": 70,
      "projects": 3
    },
    "internship_experience": true
  }'
```

**List predictions:**

```bash
curl http://127.0.0.1:8000/predictions/
```

Optional query parameters for `GET /predictions/`:

| Parameter | Description |
|-----------|-------------|
| `status` | Filter by `"Placed"` or `"Not Placed"` |
| `sort_by` | Sort by `cgpa`, `confidence`, or `created_at` |
| `order` | `asc` or `desc` (default: `desc`) |
| `min_confidence` | Minimum confidence percentage (0–100) |

## Deployment

### Docker Hub

Build and push the image for use on any Docker host:

```bash
docker build -t your-dockerhub-username/placement-predictor:latest .
docker push your-dockerhub-username/placement-predictor:latest
```

On the target server, pull the image and run with `docker compose` or pass `DATABASE_URL` and other env vars at runtime.

### AWS EC2

1. Launch an EC2 instance (Ubuntu recommended) with security group rules for ports **22**, **8000**, and **5432** (or use RDS for PostgreSQL instead of exposing 5432).
2. Install Docker and Docker Compose on the instance.
3. Clone the repo (or pull your Docker Hub image).
4. Set environment variables in `.env` or export them in the shell.
5. Run `docker compose up -d --build`.
6. Optionally place an Application Load Balancer or Nginx reverse proxy in front of the API and terminate TLS with ACM.

For production, use a managed database (e.g. Amazon RDS), store secrets in AWS Secrets Manager, and restrict security group access to the minimum required ports.

### Deploy to Render

1. **Push code to GitHub** — Commit the project (including `render.yaml`, `Dockerfile`, and `ml/model.pkl`) and push to a GitHub repository.

2. **Connect the repo on [render.com](https://render.com)** — In the Render Dashboard, create a new **Blueprint** and connect your GitHub repository. Render will read `render.yaml` and provision the `placement-api` web service.

3. **Set `DATABASE_URL`** — When prompted during Blueprint setup, provide the `DATABASE_URL` secret (marked `sync: false` in `render.yaml`). Use the connection string from Render's managed **PostgreSQL** add-on:
   - Create a PostgreSQL database in Render (or add it to your Blueprint).
   - Copy the **Internal Database URL** and paste it as the `DATABASE_URL` environment variable for `placement-api`.

4. **Deploy** — Render builds the Docker image from the root `Dockerfile` and starts the service on port `8000`. Once the deploy succeeds, the API is live at your `*.onrender.com` URL (e.g. `https://placement-api.onrender.com`). Verify with `GET /health/`.

## Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `DATABASE_URL` | Yes | PostgreSQL connection string | `postgresql://postgres:postgres@localhost:5432/placement_db` |
| `MODEL_PATH` | No | Path to the trained model file | `ml/model.pkl` |
| `MODEL_VERSION` | No | Model version reported by the health endpoint | `1.0.0` |
| `DEBUG` | No | Enable debug mode | `True` |

Copy `.env.example` to `.env` and fill in the required values before running locally or in Docker.
