# AI Decision Hub — CS50 Web Programming Final Project

**AI Decision Hub** is a full-stack, enterprise-grade decision management SaaS platform designed to assist organizations and engineering teams in systematically evaluating, risk-assessing, documenting, and auditing business decisions before execution. 

Built with **Django**, **Bootstrap 5**, **HTML5**, **CSS3**, and modular **Vanilla JavaScript (ES6+)**, the platform delivers a modern, reactive SaaS experience inspired by **Linear**, **Notion**, and **Jira**.

---

## 📌 Distinctiveness and Complexity

### Distinctiveness (Why AI Decision Hub is Unique)

AI Decision Hub was designed from the ground up to be completely distinct from all previous CS50 Web Programming projects (such as Commerce/Auctions, Network, Mail, Wiki, Search, and Pizza). 

Unlike a **Social Network** (Network), which focuses on social connections, public feeds, followers, and user profile likes, AI Decision Hub is an internal enterprise productivity tool focused on decision analysis, risk governance, audit trail logging, and project workspace evaluation. There are no public user timelines, follower graphs, or social networking dynamics.

Unlike an **E-Commerce platform** (Commerce/Auctions), which centers on product listings, shopping carts, bidding, and transaction processing, AI Decision Hub manages abstract organizational decisions, categorizing them by Risk Level (Low, Medium, High, Critical), Priority (Low, Medium, High, Urgent), Status (Draft, Under Review, Approved, Rejected, Implemented), and Impact Scores (1-100).

Unlike a **Messaging application** (Mail) or **Knowledge Base** (Wiki), AI Decision Hub incorporates multi-parameter decision filtering, file attachment processing (PDF and image uploads), automated audit trail activity logging, KPI analytics dashboard calculations, and star bookmarking across project workspaces.

### Technical Complexity

The technical complexity of AI Decision Hub spans both backend architecture and frontend engineering:

1. **Relational Database Design (8 Interconnected Models)**:
   - `User`: Custom Django User model integration managing authentication and workspace ownership.
   - `Project`: Organizational workspace container grouping related decision pipelines.
   - `Category`: Dynamic categorization system (Financial, Technical, Operational, Strategic, Legal, Marketing) with custom badge colors and icons.
   - `Decision`: Core entity containing 10 fields including Risk Level, Priority, Status, Impact Scores, and ForeignKey relations to `Project`, `Category`, and `User`.
   - `Comment`: Asynchronous discussion stream linked to specific decision entities.
   - `Attachment`: Handles file upload storage (`FileField`), metadata extraction (filename, file size in bytes), and format detection (PDF vs Image rendering).
   - `ActivityLog`: Automated audit logging system recording system events (`CREATE_PROJECT`, `CREATE_DECISION`, `EDIT_DECISION`, `DELETE_DECISION`, `ADD_COMMENT`, `UPLOAD_ATTACHMENT`, `FAVORITE_TOGGLE`).
   - `FavoriteDecision`: Unique bookmarking model with relational `unique_together` constraints preventing duplicate stars.

2. **Backend Service Layer (`services.py`)**:
   - Implements business logic separation from views.
   - Aggregates executive dashboard metrics: `total_projects`, `total_decisions`, `high_risk_decisions`, `pending_decisions`, risk distribution matrices, and audit activity streams.
   - Encapsulates system audit recording via a unified `log_activity()` helper.

3. **RESTful API & Asynchronous JavaScript Engine (`app.js`)**:
   - **Live Search & Multi-Facet Filtering**: Utilizes a debounced input handler coupled with a custom RESTful API (`GET /api/decisions/`) that filters decisions dynamically across 5 parameters (`q`, `risk`, `priority`, `status`, `category`) without reloading the page.
   - **Asynchronous Discussion Stream**: Posts comments via `POST /api/decisions/<id>/comment/` using Fetch API and async/await syntax, dynamically appending new comments into the DOM with zero page refresh.
   - **Star Favorites Toggle**: Implements `POST /api/decisions/<id>/favorite/` for instant favorite toggles with optimistic UI state updates and CSS keyframe animations (`@keyframes starPop`).
   - **File Upload Handler**: Integrates multipart form uploads for PDFs, images, and documents with live error handling and format detection.

4. **Security & Permission Architecture**:
   - Enforces strict object-level permission checks (`if entity.owner != request.user: return HttpResponseForbidden()`) across all CRUD views and API endpoints.
   - Complete protection against unauthorized modifications, unauthorized file uploads, or cross-tenant data access.
   - Comprehensive CSRF token validation on all POST/PUT/DELETE API requests.

5. **Automated Unit Test Suite (`tests.py`)**:
   - Includes 9 comprehensive automated tests verifying model relationships, cascade deletions, view access protections, search/filter RESTful API outputs, favorite toggling, and dashboard metric calculations.

---

## ✨ Key Features

- 📊 **Executive Dashboard**: KPI metric cards, risk distribution matrix (Low, Medium, High, Critical), recent decisions table, and audit stream.
- 📁 **Project Workspaces**: Create, edit, delete, and organize decision pipelines into projects.
- 🎯 **Decision Analysis Engine**: Evaluate decisions by Risk Level, Priority, Status, Impact Score, and Category.
- 🔍 **Real-Time Live Search & Multi-Filtering**: Instant search by title/description/category and multi-select filtering without page reloads.
- 💬 **AJAX Comment & Note Stream**: Post evaluation notes and team comments asynchronously.
- 📎 **File Attachment Documentation**: Upload and download PDF reports, technical spec sheets, and images.
- ⭐ **Starred Favorites**: Bookmark critical decisions for instant access on a dedicated Favorites page.
- 📜 **Audit Activity Log**: Automatic timeline recording every system action for governance and auditing.
- 👤 **User Profile & Settings**: View workspace stats and edit account information.

---

## 🛠️ Technology Stack

- **Backend Framework**: Python 3.12, Django 5.0 / 6.0
- **Frontend Framework**: HTML5, Vanilla JavaScript (ES6+, Fetch API, Async/Await)
- **UI Framework & Styling**: Bootstrap 5.3, Bootstrap Icons 1.11, Custom CSS3 (Linear/Notion theme)
- **Database**: SQLite3 (Django ORM)
- **File Storage**: Django Media Files (`FileField`)

---

## 📂 Folder Structure

```text
/Users/ahmedk.alrashed/Desktop/مشروع ٢/
├── decision_hub/                  # Core App Directory
│   ├── migrations/                # Database Migrations
│   ├── static/decision_hub/       # Static Assets
│   │   ├── styles.css             # SaaS Design Tokens & CSS
│   │   └── app.js                 # Vanilla JS Interactive Engine
│   ├── templates/decision_hub/    # HTML Templates
│   │   ├── layout.html            # Base SaaS Sidebar & Header Layout
│   │   ├── dashboard.html         # Executive Analytics Dashboard
│   │   ├── projects.html          # Projects Directory & Creation Modal
│   │   ├── project_detail.html    # Workspace Decision Board & Filters
│   │   ├── project_edit.html      # Edit Project Form
│   │   ├── project_delete_confirm.html # Delete Project Confirmation
│   │   ├── decision_detail.html   # Decision Hub Evaluation Page
│   │   ├── decision_edit.html     # Edit Decision Form
│   │   ├── decision_delete_confirm.html # Delete Decision Confirmation
│   │   ├── favorites.html         # Starred Favorites Grid
│   │   ├── activity.html          # Audit Activity Timeline
│   │   ├── profile.html           # User Profile Metadata
│   │   └── edit_profile.html      # Edit Profile Settings
│   ├── admin.py                   # Django Admin Registration
│   ├── apps.py                    # App Configuration
│   ├── forms.py                   # Django Forms (Project, Decision, Attachment, Profile)
│   ├── models.py                  # 8 Interconnected ORM Models
│   ├── services.py                # Service Layer (Audit Log & Dashboard Analytics)
│   ├── tests.py                   # Automated Test Suite
│   ├── urls.py                    # RESTful & Template URL Routing
│   └── views.py                   # Django Views & API Endpoints
├── project4/                      # Project Configuration
│   ├── settings.py                # Django Settings & Media Configuration
│   └── urls.py                    # Root URL Routing
├── seed_hub_data.py               # Demo Data Seeder Script
├── requirements.txt               # Package Dependencies
├── manage.py                      # Django Management Script
└── README.md                      # Complete Project Documentation
```

---

## 🚀 Installation & Setup Instructions

### Prerequisites
- Python 3.10+
- `pip` package manager

### Steps

1. **Clone or Navigate to the Workspace**:
   ```bash
   cd "/Users/ahmedk.alrashed/Desktop/مشروع ٢"
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Apply Database Migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Seed Baseline Categories & Demo Data**:
   ```bash
   python seed_hub_data.py
   ```

5. **Run the Test Suite**:
   ```bash
   python manage.py test decision_hub
   ```

6. **Start Development Server**:
   ```bash
   python manage.py runserver 8080
   ```

7. **Access the Application**:
   Open browser at `http://127.0.0.1:8080/`.

### Pre-seeded Demo Credentials:
- **Username**: `manager_john`
- **Password**: `password123`

---

## 🔮 Future Improvements

1. **AI Risk Assessment Integrations**: Connect OpenAI / Anthropic APIs to automatically generate risk scores based on decision descriptions.
2. **Team Collaboration & Role Permissions**: Support multi-tenant organization workspaces with Admin, Evaluator, and Viewer permissions.
3. **Export Reports**: PDF / CSV export of decision evaluations and risk matrices for executive board meetings.
