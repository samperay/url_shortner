# 🚀 FastAPI URL Shortener

A simple and scalable **URL Shortener application** built using **FastAPI** and **SQLite**, following clean architecture principles.

---

## 📌 Features

* Shorten long URLs into unique short links
* Redirect short URLs to original URLs
* Simple HTML UI using Jinja2 templates
* Clean architecture (Router → Service → Repository → DB)
* SQLite database (lightweight & easy setup)

---

## 🏗️ Architecture Overview

This project follows a layered architecture:

```
Client (HTML Form)
        ↓
Router Layer (FastAPI)
        ↓
Service Layer (Business Logic)
        ↓
Repository Layer (DB Access)
        ↓
SQLite Database
```

### 🔹 Why this architecture?

* Separation of concerns
* Easy to scale and maintain
* Clean and testable code
* Reusable components

---

## 📂 Project Structure

```
url_shortener/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── services.py
│   ├── repositories.py
│   ├── routers/
│   │   └── url_router.py
│   └── templates/
│       └── index.html
├── docs/
│   ├── context/
│   │   └── repository-context.md
│   ├── deployment/
│   │   ├── docker-desktop-kubernetes.md
│   │   └── environment-promotion.md
│   └── learning/
│       └── kubernetes-break-fix.md
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── publish-dev-image.yml
├── k8s/
│   ├── base/
│   │   ├── deployment.yaml
│   │   ├── kustomization.yaml
│   │   └── service.yaml
│   └── environments/
│       ├── dev/
│       ├── stage/
│       └── prod/
├── scripts/
│   ├── deploy-dev.sh
│   ├── deploy-prod.sh
│   ├── deploy-stage.sh
│   └── start.sh
├── tests/
├── requirements.txt
└── README.md
```

---

## ⚙️ Tech Stack

* **Backend**: FastAPI
* **Database**: SQLite
* **ORM**: SQLAlchemy
* **Frontend**: HTML (Jinja2 Templates)
* **Server**: Uvicorn

---

## 🛠️ Installation

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd url_shortener
```

### 2. Create virtual environment

```bash
curl -Ls https://astral.sh/uv/install.sh | sh
uv --version
uv venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the Application

```bash
./scripts/start.sh
```

Open in browser:

```
http://127.0.0.1:8000
```

---

## 🐳 Local Docker Desktop Deployment

The deployment scripts are for manual local testing against Docker Desktop
Kubernetes. They build the local image `url-shortener:dev`, apply the selected
Kustomize overlay, and override the Deployment to use the local Docker Desktop
image.

```bash
./scripts/deploy-dev.sh
kubectl port-forward svc/url-shortener 30080:80 -n url-shortener-dev
```

Stage and production local overlays are available through:

```bash
./scripts/deploy-stage.sh
./scripts/deploy-prod.sh
```

---

## 🚢 Dev GitOps Deployment

The `dev` branch is deployed through Docker Hub and Argo CD.

When a commit lands on `dev`, `.github/workflows/publish-dev-image.yml`:

1. Builds the Docker image.
2. Tags it as `sunlnx/url-shortener:dev_<short_commit_id>`.
3. Pushes it to Docker Hub.
4. Updates `k8s/environments/dev/kustomization.yaml` with the new tag.
5. Commits the tag update back to `dev`.

Argo CD watches the `dev` branch and deploys the updated image to the
`url-shortener-dev` namespace.

Required GitHub repository secrets:

```text
DOCKER_HUB_LOGIN
DOCKER_HUB_TOKEN
```

---

## 🌐 Application Flow

1. User enters a long URL in the UI
2. Request is sent to `/shorten`
3. Service generates a unique short code
4. Data is stored in SQLite
5. Short URL is displayed
6. Clicking short URL redirects to original URL

---

## 🔁 API Endpoints

### 1. Home Page

```
GET /
```

* Displays HTML form

---

### 2. Create Short URL

```
POST /shorten
```

* Accepts form input
* Returns shortened URL

---

### 3. Redirect to Original URL

```
GET /{short_code}
```

* Redirects to original URL

---

## 🗄️ Database Schema

Table: `url_mappings`

| Column       | Type     | Description             |
| ------------ | -------- | ----------------------- |
| id           | Integer  | Primary key             |
| original_url | String   | Long URL                |
| short_code   | String   | Unique short identifier |
| created_at   | DateTime | Timestamp               |

---

## 🧠 Key Components Explained

### 🔹 Router Layer

Handles HTTP requests and responses.

### 🔹 Service Layer

Contains business logic:

* Generate short codes
* Handle duplicates
* Validate logic

### 🔹 Repository Layer

Handles all database interactions.

### 🔹 Database Layer

SQLite database using SQLAlchemy ORM.

---

## 💡 Example

### Input

```
https://www.google.com/search?q=fastapi+url+shortener
```

### Output

```
http://127.0.0.1:8000/aB12Cd
```

Clicking the short URL redirects to the original URL.

---

## 🔐 Future Improvements

* Custom short URLs
* Expiry for links
* Click analytics
* Redis caching
* Rate limiting
* Authentication & user accounts
* Kubernetes deployment (fits your learning path 🚀)

---

## 🧪 Testing Ideas

* Test duplicate URL handling
* Test invalid URL input
* Test redirect functionality
* Load test short URL generation

---

## 📚 Documentation

Additional project notes are organized under `docs/`:

* [Repository context](docs/context/repository-context.md)
* [Docker Desktop Kubernetes deployment](docs/deployment/docker-desktop-kubernetes.md)
* [Environment promotion flow](docs/deployment/environment-promotion.md)
* [Kubernetes break/fix learning path](docs/learning/kubernetes-break-fix.md)

---

## 📦 Deployment Ideas

* Dockerize the app
* Deploy on:

  * AWS EC2 / ECS
  * IBM Cloud Code Engine
  * Kubernetes (Ingress + Service)

---

## 👨‍💻 Author

**Sunil**
SRE | DevOps | Automation Engineer

---
