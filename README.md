# student-ml-api

A FastAPI prediction service demonstrating a complete, professional MLOps workflow: feature branches, Pull Requests, automated CI, branch-protected merges, semantic versioning, Docker containerization, and GitHub Container Registry (GHCR) publishing.

📄 **Full project writeup, design decisions, and evidence:** see [`Document.md`](Document.md)

---

## Quick Start — Run Locally

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
pip install pytest httpx

python -m pytest                # run tests
uvicorn app:app --reload        # start the API
```

Visit `http://127.0.0.1:8000/docs` for interactive API docs.

## Quick Start — Run via Docker

**Build and run locally:**
```bash
docker build -t student-ml-api:local .
docker run -d --name student-ml-api -p 5000:5000 student-ml-api:local
curl http://localhost:5000/health
```

**Or pull the published image:**
```bash
docker pull ghcr.io/abdullah-07s/student-ml-api:latest
docker run -d --name student-ml-api -p 5000:5000 ghcr.io/abdullah-07s/student-ml-api:latest
curl http://localhost:5000/health
```

---

## API Endpoints

**`GET /health`**
```json
{
  "status": "healthy",
  "application": "student-ml-api",

**`POST /predict`**
```json
// Request
{ "value": 10 }

// Response
{ "input": 10, "prediction": 20 }
```

---

## Repository Structure

```
student-ml-api/
├── app.py                      # FastAPI application
├── requirements.txt            # Runtime dependencies (fastapi, uvicorn)
├── Dockerfile                  # Production container image
├── .dockerignore
├── VERSION                     # Single source of truth for app version
├── tests/
│   └── test_app.py             # 4 automated tests
├── .github/workflows/
│   ├── ci.yml                  # Runs on every PR: tests + docker build validation
│   └── release.yml             # Runs on version tags: build, tag, publish to GHCR
├── Document.md                 # Full submission writeup
└── VIVA_PREP.md                # Viva question prep (if included)
```

---

## Development Workflow

1. Branch off `main`: `git checkout -b feature/your-feature`
2. Make changes, commit with conventional messages (`feat:`, `fix:`, `test:`, `chore:`)
3. Push and open a Pull Request into `main`
4. CI (`ci.yml`) runs automatically — tests must pass and the Docker image must build successfully
5. Merge only once checks are green (`main` is branch-protected — direct pushes are blocked)
6. To release: tag the merge commit with a semantic version and push the tag
   ```bash
   git tag v1.2.0
   git push origin v1.2.0
   ```
   This triggers `release.yml`, which builds, versions, and publishes the image to GHCR automatically.

---

## Container Registry

Images are published to GitHub Container Registry:

```
ghcr.io/abdullah-07s/student-ml-api:<version>
ghcr.io/abdullah-07s/student-ml-api:latest
ghcr.io/abdullah-07s/student-ml-api:<commit-sha>
```

Browse all published versions: https://github.com/Abdullah-07s?tab=packages

---

## License

Coursework submission — MLOps Assignment 1.
