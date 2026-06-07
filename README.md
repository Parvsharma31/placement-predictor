# Student Placement Prediction API

Production-style REST API that predicts student placement outcomes using a scikit-learn model, with PostgreSQL persistence and Docker support.

[![Live Demo](https://img.shields.io/badge/demo-live-success)](https://placement-api-t850.onrender.com/docs)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-009688?logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4.2-F7931E?logo=scikit-learn&logoColor=white)

## Live Demo

The API is deployed on Render and ready to use:

| Resource | URL |
|----------|-----|
| **Interactive docs** | [https://placement-api-t850.onrender.com/docs](https://placement-api-t850.onrender.com/docs) |
| **Health check** | [https://placement-api-t850.onrender.com/health/](https://placement-api-t850.onrender.com/health/) |
| **GitHub repo** | [https://github.com/Parvsharma31/placement-predictor](https://github.com/Parvsharma31/placement-predictor) |

> **Note:** On Render's free tier, the service sleeps after ~15 minutes of inactivity. The first request after sleep may take 30–60 seconds.

## Features

- **ML prediction** — Random Forest classifier trained on synthetic student data
- **CRUD API** — Create, read, update, and delete prediction records
- **Pydantic validation** — Strict request/response schemas with field constraints
- **Computed fields** — `placement_readiness_score` derived from student inputs
- **PostgreSQL storage** — Predictions persisted with SQLAlchemy ORM
- **Docker support** — Multi-container setup with `docker compose`
- **Cloud deployment** — One-click deploy to Render via `render.yaml`

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
│   │   └── response_schema.py  # Pydantic response models
│   ├── services/
│   │   └── predictor.py        # Model loading and inference
│   └── database/
│       ├── connection.py       # SQLAlchemy engine and session
│       └── models.py           # ORM models
├── ml/
│   ├── train_model.py          # Model training script
│   └── model.pkl               # Trained pipeline
├── .env                        # Local environment variables (not committed)
├── .env.example                # Environment template
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── render.yaml                 # Render Blueprint (IaC)
└── README.md
```

## Quick Start (Use the Live API)

No setup required — open the [Swagger UI](https://placement-api-t850.onrender.com/docs) and try **POST `/predictions/predict`** with this body:

```json
{
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
}
```

Or from the terminal:

```bash
curl -X POST https://placement-api-t850.onrender.com/predictions/predict \
  -H "Content-Type: application/json" \
  -d '{
    "academic": {"cgpa": 8.5, "aptitude_score": 78},
    "skills": {"communication_score": 82, "dsa_score": 70, "projects": 3},
    "internship_experience": true
  }'
```

### Share with others

Send the docs link — anyone can try the API in their browser:

> **Student Placement Prediction API**  
> Try it: [https://placement-api-t850.onrender.com/docs](https://placement-api-t850.onrender.com/docs)

For developers, share the base URL `https://placement-api-t850.onrender.com` and the GitHub repo.

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/Parvsharma31/placement-predictor.git
cd placement-predictor
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

### 5. Start PostgreSQL locally

Ensure PostgreSQL is running and the `placement_db` database exists, then verify your `DATABASE_URL` in `.env`.

### 6. Train the model

```bash
python ml/train_model.py
```

This generates `ml/model.pkl` and prints a classification report on the test set.

### 7. Run the API

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

**Create a prediction (local):**

```bash
curl -X POST http://127.0.0.1:8000/predictions/predict \
  -H "Content-Type: application/json" \
  -d '{
    "academic": {"cgpa": 8.5, "aptitude_score": 78},
    "skills": {"communication_score": 82, "dsa_score": 70, "projects": 3},
    "internship_experience": true
  }'
```

**Create a prediction (live):**

```bash
curl -X POST https://placement-api-t850.onrender.com/predictions/predict \
  -H "Content-Type: application/json" \
  -d '{
    "academic": {"cgpa": 8.5, "aptitude_score": 78},
    "skills": {"communication_score": 82, "dsa_score": 70, "projects": 3},
    "internship_experience": true
  }'
```

**List predictions:**

```bash
curl https://placement-api-t850.onrender.com/predictions/
```

Optional query parameters for `GET /predictions/`:

| Parameter | Description |
|-----------|-------------|
| `status` | Filter by `"Placed"` or `"Not Placed"` |
| `sort_by` | Sort by `cgpa`, `confidence`, or `created_at` |
| `order` | `asc` or `desc` (default: `desc`) |
| `min_confidence` | Minimum confidence percentage (0–100) |

### Sample Response

```json
{
  "id": 1,
  "placement_prediction": "Placed",
  "confidence": 99.0,
  "probabilities": {"placed": 99.0, "not_placed": 1.0},
  "placement_readiness_score": 96.9,
  "created_at": "2026-06-07T05:34:49.648970"
}
```

## Deployment

### Deploy to Render (recommended)

The project includes a `render.yaml` Blueprint that provisions both the API and a managed PostgreSQL database.

1. **Push code to GitHub** — [https://github.com/Parvsharma31/placement-predictor](https://github.com/Parvsharma31/placement-predictor)
2. **Create a Blueprint** on [render.com](https://render.com) and connect the repo
3. **Apply** — Render creates:
   - `placement-db` — PostgreSQL database
   - `placement-api` — Docker web service
4. **`DATABASE_URL` is wired automatically** via `fromDatabase` in `render.yaml` — no manual entry needed in most cases
5. **Verify** — Visit `https://YOUR-SERVICE.onrender.com/health/` and confirm `"database": "connected"`

If prompted manually for `DATABASE_URL`, paste the **Internal Database URL** from the `placement-db` service in the Render dashboard.

### Docker Hub

Build and push the image for use on any Docker host:

```bash
docker build -t your-dockerhub-username/placement-predictor:latest .
docker push your-dockerhub-username/placement-predictor:latest
```

### AWS EC2

1. Launch an EC2 instance (Ubuntu recommended) with security group rules for ports **22**, **8000**, and **5432** (or use RDS for PostgreSQL).
2. Install Docker and Docker Compose on the instance.
3. Clone the repo and set environment variables in `.env`.
4. Run `docker compose up -d --build`.
5. Optionally place an ALB or Nginx reverse proxy in front of the API.

## Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `DATABASE_URL` | Yes | PostgreSQL connection string | `postgresql://postgres:postgres@localhost:5432/placement_db` |
| `MODEL_PATH` | No | Path to the trained model file | `ml/model.pkl` |
| `MODEL_VERSION` | No | Model version reported by the health endpoint | `1.0.0` |
| `DEBUG` | No | Enable debug mode | `True` |

Copy `.env.example` to `.env` and fill in the required values before running locally or in Docker.

## License

MIT — feel free to use, share, and build on this project.
