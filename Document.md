# student-ml-api — Assignment 1 Submission

**Repository:** https://github.com/Abdullah-07s/student-ml-api
**Registry:** https://github.com/Abdullah-07s?tab=packages (`ghcr.io/abdullah-07s/student-ml-api`)

---

## 1. Project Overview

`student-ml-api` is a FastAPI-based prediction service built to demonstrate a complete, professional MLOps CI/CD workflow: feature branches → Pull Requests → automated CI → branch-protected merge → semantic version tags → automated Docker builds → GitHub Container Registry (GHCR) publishing.

**Stack:** Python 3.11, FastAPI, Uvicorn, pytest, Docker, GitHub Actions, GHCR.

---

## 2. Repository Structure

```
student-ml-api/
├── app.py
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── VERSION
├── tests/
│   └── test_app.py
└── .github/
    └── workflows/
        ├── ci.yml
        └── release.yml
```

---

## 3. Application (Part 1–2)

- `GET /health` returns application status, name, `application_version` (read dynamically from the `VERSION` file), and `model_version` (a static constant representing where real model-lifecycle metadata would live).
- `POST /predict` accepts `{"value": <int>}` and returns `{"input": ..., "prediction": <value * 2>}`.
- **Design decision:** version is read from `VERSION` at request time via a path resolved relative to `app.py`'s own location (`os.path.dirname(os.path.abspath(__file__))`), not the process's working directory — this avoids "works on my machine" bugs across local runs, pytest, and Docker, where the working directory differs.
- **4 automated tests** in `tests/test_app.py`: health check, successful prediction, missing input (422), invalid input type (422).

---

## 4. Git Workflow & Pull Requests (Part 3–4, 8)

All development happened on feature branches, merged into `main` exclusively via reviewed, CI-gated Pull Requests. Direct pushes to `main` are blocked by branch protection (Part 7).

| PR | Branch | Purpose |
|----|--------|---------|
| #1 | `feature/prediction-api` | Initial app, tests, requirements |
| #2 | `feature/release-workflow` | Real GHCR release pipeline |
| #3 | `feature/model-metadata` | v1.1.0 — model_version field |
| #4 | `feature/oci-labels` | OCI image labels for traceability |
| #5 | `fix/release-yaml-indentation` | Bugfix — broken YAML from OCI labels PR |
| #6 | `feature/commit-sha-tag` | Commit-SHA image tagging |
| #7 | `demo/docker-build-failure` | Deliberate Docker build failure demonstration (Part 26) |
| #8 | `docs/submission-writeup-v2` | Submission writeup (Document.md) |
| #9 | `Abdullah-07s-patch-1` | Project README |

**Merge strategy: Merge Commit**, chosen deliberately over squash/rebase, because:
1. It preserves the deliberate test-failure-then-fix commit pair from Part 6 as real, individually inspectable history rather than collapsing it.
2. Part 21 (traceability) asks for a specific merge commit SHA per release — a merge commit gives an explicit, single SHA representing "this PR landed here," which pairs cleanly with the tag-per-release model used throughout.

---

## 5. GitHub Actions CI (Part 5–6)

`ci.yml` triggers on every Pull Request targeting `main`. Two jobs:
1. **`test`** — checkout, Python 3.11 setup, install dependencies, `python -m pytest`.
2. **`docker-build-check`** — `needs: test` (fail-fast: skipped entirely if tests fail), builds the Docker image to validate it compiles. **No push occurs here.**

**Deliberate failure demonstration (Part 6):** `test_health`'s assertion was changed to expect `"status": "wrong"`, committed and pushed — CI failed (exit code 1), `docker-build-check` was correctly skipped due to the `needs: test` dependency. The assertion was then reverted and pushed again — CI passed. This confirms CI genuinely gates merges rather than being decorative.

---

## 6. Branch Protection (Part 7)

`main` is protected with:
- ✅ Require a pull request before merging
- ⬜ Require approvals (intentionally unchecked — solo project; in a team setting this would require 1+ reviewer)
- ✅ Require status checks to pass before merging (`test`, `docker-build-check`)
- ✅ Require branches to be up to date before merging
- ✅ Do not allow bypassing the above settings (applies even to repo admins)

**Justification:** PR + passing CI are mandatory regardless of role, ensuring no untested code reaches `main`. Approvals were left off only because this is a solo submission.

---

## 7. Dockerfile & Containerization (Part 9–11, 23)

```dockerfile
FROM python:3.11-slim

ARG APP_VERSION=unknown
ARG GIT_COMMIT=unknown
ARG BUILD_DATE=unknown

LABEL org.opencontainers.image.version="${APP_VERSION}"
LABEL org.opencontainers.image.revision="${GIT_COMMIT}"
LABEL org.opencontainers.image.source="https://github.com/abdullah-07s/student-ml-api"
LABEL org.opencontainers.image.created="${BUILD_DATE}"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py VERSION .

EXPOSE 5000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]
```

**Key decisions:**
- Specific base image (`python:3.11-slim`), never `latest` — reproducibility.
- `COPY requirements.txt` → `pip install` → `COPY app.py` ordering (not `COPY . .` first) — see Part 25 for the measured caching benefit.
- `--host 0.0.0.0` (not `127.0.0.1`) — required for the container's port to be reachable from outside; binding to loopback is a documented common failure mode (Part 26).
- OCI labels carry version/commit/build-date metadata directly inside the image, populated via build-args from `release.yml`.

**Local inspection (Part 11) — recorded values:**
- Container ID: `dbf48365156a`
- Image ID: `6807275166c6`
- Exposed port: `5000/tcp`
- Running command: `uvicorn app:app --host 0.0.0.0 --port 5000`
- Working directory: `/app`

---

## 8. `.dockerignore` (Part 9)

```
.git
.github
__pycache__
*.pyc
.venv
.env
tests/
```

Note: `.env` is excluded here as a defensive default, even though this project never uses one — all secrets (GHCR authentication) are handled via GitHub Actions' auto-injected `GITHUB_TOKEN`, never via files.

---

## 9. Container Registry & Semantic Versioning (Part 12–16)

**Registry:** GitHub Container Registry (GHCR), chosen over Docker Hub because it authenticates automatically via the workflow's built-in `GITHUB_TOKEN` — no manual PAT generation or secret storage required.

**`release.yml`** triggers only on tags matching `v*.*.*` (never on PRs or branch pushes). Pipeline: checkout → test → GHCR login → derive version from tag name (`${GITHUB_REF_NAME#v}`, never hardcoded) → build with OCI label build-args → tag as `<version>`, `latest`, and short commit SHA → push all three.

**Published releases:**

| Version | Tag | Merge Commit | Image Digest |
|---|---|---|---|
| 1.0.0 | `v1.0.0` | `baf7530` | `sha256:90281b5ce5a7b490a8a5f8282ccb7d5358ab2567c5c3bfb61d6998ed3d476268` |
| 1.1.0 | `v1.1.0` | `47472ce` | `sha256:2b0f02ab110b55f3adac822417e6913ba3f7941935818065d7489fbe04bac74c` |
| 1.1.1 | `v1.1.1` | `c5ee6b3` | `sha256:81b5b1d7986a12f3db78fef852d45a3e9087bca8bb70867f16d6fd13a055f626` |
| 1.1.2 | `v1.1.2` | `0478f7b` | `sha256:7c7683c6ffb6932ec1c3c813d0079e822f4543cdbc2c58cbeefd8e1c9a6059ba` |

`latest` correctly tracks the most recent release (verified at each step); older versions remain independently pullable.

**Note on `VERSION` file vs. image tag:** the running application's `/health` endpoint reports whatever the `VERSION` file contained at build time, which is independent of the Docker image's external tag or the Git tag used to trigger the release. Releases `v1.1.1` and `v1.1.2` were pipeline-only changes (a YAML indentation fix and the addition of commit-SHA tagging, respectively) — no application code changed, so the `VERSION` file's content intentionally remained `1.1.0` for those releases. This was confirmed during a fresh-clone dry run: pulling `ghcr.io/abdullah-07s/student-ml-api:latest` (digest matching the `v1.1.2` release) correctly returns `"application_version":"1.1.0"` in `/health`, since the application itself has not changed since v1.1.0. This is expected behavior, not a bug — it demonstrates that the image tag (tracking the release/pipeline) and the application version (tracking actual code behavior) are able to move independently, which is a deliberate and desirable property once a project has a real model-serving lifecycle (see Viva Q15).

---

## 10. Reproducibility (Part 17)

Demonstrated by deleting the local `1.0.0` image entirely (`docker rmi`), pulling it fresh from GHCR, running it, and confirming `/health` returned identical output — proving the registry artifact is portable across environments without rebuilding.

---

## 11. Version 1.1.0 Development (Part 18–19)

`/health` was extended to return `application_version` and `model_version` independently, following the identical PR → CI → review → merge → tag → release cycle used for v1.0.0. This demonstrates the workflow is repeatable, not a one-off.

**Design note:** `model_version` is deliberately a separate hardcoded constant, not folded into the `VERSION` file, because in a real system a model's lifecycle (retraining, evaluation, promotion) is independent of the API's release cadence — conflating them would make it impossible to ship an API fix without implying a model change, or vice versa (see Part 22-style reasoning, Viva Q15).

---

## 12. Rollback Exercise (Part 20)

Simulated a production issue in `v1.1.0`: stopped and removed the running `1.1.0` container, then started `1.0.0` directly from the registry (`docker run ... ghcr.io/.../student-ml-api:1.0.0`) — no source code changes, no rebuild. `/health` confirmed the rollback.

**Why this beats a `git clone && pip install && python app.py` rollback:** the registry-based approach runs the exact same bytes that were built and tested in CI — a known-good, immutable artifact. A source-based rollback re-triggers a fresh build, which risks pulling different transitive dependency versions (since `requirements.txt` doesn't pin every transitive package), depends on the build machine's environment matching the original, and takes materially longer. During an active incident, `docker run` against a cached image is seconds; a fresh clone-and-build is minutes, with non-zero risk of building something subtly different from what was actually running before.

---

## 13. Traceability (Part 21)

**Required chain for v1.1.0:**

| Stage | Value |
|---|---|
| Pull Request | #3 |
| Merge Commit SHA | `47472ce` |
| Git Tag | `v1.1.0` |
| Docker Image | `student-ml-api:1.1.0` |
| Image Digest | `sha256:2b0f02ab110b55f3adac822417e6913ba3f7941935818065d7489fbe04bac74c` |

**Additional layer — OCI labels (from v1.1.1 onward):** every image embeds its own provenance, independently verifiable without external documentation:

```json
{
  "org.opencontainers.image.version": "1.1.2",
  "org.opencontainers.image.revision": "0478f7b4c52d6ff6f7d689b2b51a55881ba56480",
  "org.opencontainers.image.source": "https://github.com/abdullah-07s/student-ml-api",
  "org.opencontainers.image.created": "2026-09-08T20:29:42Z"
}
```

The v1.1.2 image is traceable to its commit three independent ways: Git tag history, the Docker image tag itself (`0478f7b`, matching the merge commit short SHA), and the OCI label baked into the image — any one of these being lost, the others still confirm origin.

---

## 14. Why CI Should Not Publish From Every PR (Part 22)

A Pull Request is proposed, unreviewed code. Publishing from every PR would: pollute the registry with images from exploratory or intentionally-broken commits (e.g. the Part 6 demonstration); let unreviewed code reach an artifact store implicitly trusted for deployment, undermining branch protection; produce ambiguously-versioned images since PRs carry no semantic version; and multiply the exposure of registry credentials across many more workflow runs than necessary. Separating `ci.yml` (build/test validation on PRs) from `release.yml` (publish only on tags) means CI answers "does this work?" while release answers "should this specific, reviewed, tagged version ship?" — two different questions gated by two different triggers.

---

## 15. OCI Labels & Commit-SHA Tags (Part 23–24)

Added `ARG`/`LABEL` pairs to the Dockerfile for version, git commit, source, and build date, populated via `--build-arg` in `release.yml` using `github.sha` and a UTC timestamp. Additionally, each release is tagged with the short (7-char) commit SHA alongside the semantic version and `latest`, giving a third, effectively-immutable pointer from image to source commit — verified end-to-end in v1.1.2 (see Section 13).

**Benefit of a commit-specific tag:** semantic version tags and `latest` are both nominally re-taggable; a commit-SHA tag is tied directly to immutable Git history, so it remains a reliable, permanent reference even if a version tag were ever corrected or `latest` moves forward.

---

## 16. Docker Build Cache Analysis (Part 25)

Two experiments were run:

**Experiment 1 — modify `app.py` only:** rebuild showed `WORKDIR`, `COPY requirements.txt .`, and `RUN pip install` all `CACHED`; only the final `COPY app.py VERSION .` layer re-executed (0.8s vs. a full ~40s dependency install).

**Experiment 2 — modify `requirements.txt`:** rebuild invalidated `COPY requirements.txt .` **and every subsequent layer**, including a full re-run of `pip install`.

**Conclusion:** Docker's cache is order- and content-dependent — invalidating one layer forces every layer after it to rebuild, regardless of whether their own instructions changed. This is exactly why `COPY requirements.txt . / RUN pip install / COPY app.py .` (dependencies before code) is preferable to `COPY . . / RUN pip install`: application code changes far more often than dependencies, so this ordering means most day-to-day builds only re-run the cheap final copy step instead of a full dependency reinstall — materially faster CI and local iteration.

---

## 17. Failure Analysis (Part 26)

**Failure 1 — Failed pytest in CI**
- **Symptom:** `test_health` assertion changed to expect `"status": "wrong"`; CI job `test` failed with exit code 1, `docker-build-check` was correctly skipped.
- **Root cause:** Deliberately introduced incorrect assertion, to demonstrate CI gating (Part 6).
- **Evidence:** GitHub Actions run showing red `test` job, grey/skipped `docker-build-check`.
- **Correction:** Reverted the assertion to the correct expected value; CI passed on the next push.

**Failure 2 — Failed Docker build from a malformed `requirements.txt`**
- **Symptom:** `docker build` failed at `RUN pip install` with `ERROR: Invalid requirement: 'uvicorn==0.52.4# cache test comment'`.
- **Root cause:** A shell append (`echo ... >> requirements.txt`) appended text onto the same line as the existing `uvicorn` version pin rather than starting a new line, corrupting the requirement specifier.
- **Evidence:** Full build log showing exit code 1 and pip's exact parser error.
- **Correction:** Reverted via `git checkout requirements.txt`, restoring the last committed, valid version — illustrating why source-controlled dependency files plus CI validation on every PR catch this class of error before it can reach `main`.

**Failure 3 (bonus) — Broken CI YAML from indentation error**
- **Symptom:** `release.yml`'s "Build Docker image" step used inconsistent indentation after being edited for OCI label support, producing GitHub's "Invalid workflow file... not enough info to determine what you meant" error, breaking the entire workflow's parseability.
- **Root cause:** The `run: |` block for that one step was indented at 2/4 spaces instead of matching the 8-space indentation of every other step, un-nesting it from its parent `- name:` key.
- **Evidence:** GitHub Actions "Invalid workflow file" annotation citing the exact line and column.
- **Correction:** Corrected indentation to match sibling steps exactly; verified by re-running the workflow successfully (PR #5, later validated end-to-end with the `v1.1.1` release).

---

## 18. Fresh-Clone Verification (Final Dry Run)

To confirm the entire submission works exactly as documented — not just "on the development machine" — the repository was cloned fresh into a separate, untouched directory and every documented workflow was re-run verbatim:

1. `git clone` — succeeded, full history and all four version tags (`v1.0.0`–`v1.1.2`) present and correctly linked to their merge commits.
2. Local setup (venv, `pip install -r requirements.txt`, `pip install pytest httpx`) — succeeded with no manual fixes.
3. `python -m pytest` — 4/4 tests passed immediately.
4. `uvicorn app:app --reload` — started cleanly, endpoints functioned as documented.
5. `docker build` — succeeded, all layers cached correctly from the prior local build state.
6. Local container run + `curl /health` — returned the correct response.
7. `docker pull ghcr.io/abdullah-07s/student-ml-api:latest` — succeeded; the pulled digest (`sha256:7c7683c6...a6059ba`) matched the recorded `v1.1.2` digest exactly.
8. Running the pulled registry image — `/health` responded correctly (see the VERSION-vs-tag note above for why `application_version` reads `1.1.0`).

This confirms the submission is reproducible by a third party from nothing but the public repository and registry — no hidden local state or undocumented steps.

---

## 19. How to Run Locally

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install pytest httpx
python -m pytest
uvicorn app:app --reload
```

## 20. How to Run via Docker

```powershell
docker build -t student-ml-api:local .
docker run -d --name student-ml-api -p 5000:5000 student-ml-api:local
curl.exe http://localhost:5000/health
```

## 21. How to Pull the Published Image

```powershell
docker pull ghcr.io/abdullah-07s/student-ml-api:latest
docker run -d --name student-ml-api -p 5000:5000 ghcr.io/abdullah-07s/student-ml-api:latest
```
