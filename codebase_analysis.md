# Comprehensive Codebase Analysis

## 1. Project Overview

*   **Project Name:** EFYS - Enerji Faturalandırma ve Yönetim Sistemi (Energy Billing and Management System)
*   **Project Type:** Web Application (Monolithic) & Batch Processing System
*   **Tech Stack:**
    *   **Backend:** Python 3.10+ (Flask Framework)
    *   **Database:** PostgreSQL (using `psycopg2` driver)
    *   **Frontend:** Server-Side Templating (Jinja2) + Tailwind CSS + Vanilla JavaScript
    *   **Design System:** Custom "OSOS Design System" (Glassmorphism + Dark/Light modes)
*   **Architecture Pattern:** MVC (Model-View-Controller) adapted for Flask (Blueprints for modularity, Service layer for logic).
*   **Current Phase:** Phase 1 (Infrastructure & Basic Modules) - transitioning to Phase 2 (Dashboard & Billing).

## 2. Detailed Directory Structure Analysis

### Root Directory (`/`)
*   **`app.py`**: The main entry point of the Flask application. Initializes the app, registers blueprints, and sets up error handlers.
*   **`config.py`**: Configuration classes (Development, Production) managing environment variables and settings like DB connection strings.
*   **`requirements.txt`**: Python dependency manifest.

### `routes/` (Controllers/Views)
Contains Flask Blueprints defining the application's URL routes. Each file corresponds to a functional module:
*   **`dashboard.py`**: Main dashboard view.
*   **`billing.py`**: Billing operations (invoice calculation, period management).
*   **`readings.py`**: Meter reading management (manual/scheduled).
*   **`monitoring.py`**: Energy monitoring views (instant data, load profiles).
*   **`subscribers.py`**: Customer/Subscriber management.
*   **`reports.py`**: Reporting endpoints.
*   **`settings.py`**: System configuration routes.
*   **`smart_systems.py`**: Advanced features (AI/ML placeholders).

### `services/` (Model/Business Logic)
Contains the core business logic and data access layer.
*   **`database.py`**: The primary service class (`DatabaseService`). It handles direct PostgreSQL connections and executes raw SQL queries. This layer acts as both the Data Access Object (DAO) and Service layer.
*   **`database_extensions.py`**: Likely helper functions or extensions for DB operations.

### `templates/` (Views)
Jinja2 HTML templates mirroring the `routes` structure.
*   **`base.html`**: The master layout template containing common elements (head, scripts, structure).
*   **`components/`**: Reusable UI parts (sidebar, header, footer, cards).
*   **`dashboard/`, `billing/`, etc.**: Module-specific pages.

### `static/` (Assets)
*   **`css/`**: Stylesheets (Tailwind output/custom CSS).
*   **`js/`**: Client-side JavaScript.
*   **`img/`**: Static images.

### `database/` (Data Layer)
*   **`schema.sql`**: The complete DDL (Data Definition Language) for the PostgreSQL database.
*   **`seed_gonen_subscribers.sql`**: Seed data for initializing the system with demo/production data.

### `design-system/`
Contains design specifications and documentation.
*   **`efys---enerji-faturalandırma-sistemi/`**: Documentation related to the specific design system used.

### `DOCS/` (Documentation)
Comprehensive project documentation.
*   **`PLAN.md`**: Project roadmap and status.
*   **`EFYS_MENU_STRUCTURE.md`**: Detailed feature map and menu hierarchy.
*   **`EFYS_COMPREHENSIVE_ANALYSIS.md`**: Analysis of the system (likely the source or precursor to this document).

## 3. File-by-File Breakdown

### Core Application Files
*   **`app.py`**: Configures Flask `create_app` factory. **Note:** SQLAlchemy is currently commented out in favor of raw SQL in services.
*   **`routes/__init__.py`**: Blueprint registration logic.

### Configuration Files
*   **`config.py`**: Defines `DevelopmentConfig` and `ProductionConfig`. Hardcoded DB credentials found (Security Risk).
*   **`.env`** (implied): Used by `python-dotenv` to load secrets.

### Data Layer
*   **`services/database.py`**: **CRITICAL FILE.** Contains all SQL queries for the application. Implements `get_dashboard_stats`, `calculate_invoice`, `get_meter_indexes`, etc.
*   **`database/schema.sql`**: Defines tables: `subscribers`, `meters`, `readings` (15-min data), `tariffs`, `invoices`, `users`, `system_logs`.

### Frontend/UI
*   **`templates/base.html`**: Defines the main application shell.
*   **`templates/components/sidebar.html`**: Implements the navigation structure defined in `EFYS_MENU_STRUCTURE.md`.

### DevOps/Deployment
*   No Dockerfile or CI/CD configuration files (GitHub Actions, GitLab CI) were found in the root.
*   **`requirements.txt`**: Lists `gunicorn`, `psycopg2-binary`, `Flask`.

## 4. API Endpoints Analysis
The application currently uses **Server-Side Rendering (SSR)**. There is no distinct REST API returning JSON for a separate frontend.
*   **Routes** return `render_template` (HTML).
*   **Interaction:** Form submissions (POST) and URL navigation (GET).
*   **Future:** `DOCS/PLAN.md` mentions "Phase 4: Backend API" suggesting a transition to or addition of JSON endpoints later.

## 5. Architecture Deep Dive

### Overall Architecture
The system is a **classic Monolithic Web Application**.
*   **Request Cycle:** Browser -> Flask Route -> Service Layer (SQL Query) -> Database -> Service Layer (Dict) -> Flask Route -> Jinja2 Template -> Browser.

### Key Patterns
1.  **Service Layer Pattern:** `services/database.py` encapsulates all data logic. Routes do not query the DB directly.
2.  **Raw SQL:** The project explicitly chooses raw SQL over ORM (SQLAlchemy is disabled). This suggests a preference for performance optimization or specific complex queries (like time-series aggregations on reading data) that are harder to express in ORM.
3.  **Factory Pattern:** `create_app` in `app.py` allows for easy testing and multiple configurations.

### Data Flow
1.  **Ingestion:** Meter readings are likely ingested via a separate process (referenced as `reading_tasks` in plans) into the `readings` table.
2.  **Processing:** 15-minute interval data is aggregated on-the-fly for dashboards and billing.
3.  **Billing:** `calculate_invoice` function in `database.py` performs complex calculations combining `readings`, `tariffs`, and `subscribers`.

## 6. Environment & Setup Analysis

*   **Runtime:** Python 3.10+
*   **Environment Variables Required:**
    *   `FLASK_ENV`
    *   `DATABASE_URL` (PostgreSQL connection string)
    *   `SECRET_KEY`
*   **Installation:**
    1.  `pip install -r requirements.txt`
    2.  Setup PostgreSQL database.
    3.  Run `database/schema.sql` and seeds.
    4.  `python app.py` (Dev) or `gunicorn app:app` (Prod).

## 7. Technology Stack Breakdown

*   **Web Framework:** **Flask 3.0.0** - Lightweight, flexible.
*   **Database:** **PostgreSQL** - Robust relational DB, excellent for time-series data (readings).
*   **DB Driver:** **psycopg2-binary** - Standard, high-performance PostgreSQL adapter.
*   **Templating:** **Jinja2** - Standard Flask templating.
*   **Styling:** **Tailwind CSS** - Utility-first CSS framework (likely via CDN or pre-compiled assets in `static/css`).
*   **PDF Generation:** **WeasyPrint** & **ReportLab** - Used for invoice generation.
*   **Excel:** **openpyxl** - For report exports.

## 8. Visual Architecture Diagram

```mermaid
graph TD
    User[Web Browser] <--> |HTTP/HTML| LoadBalancer[Nginx/Gunicorn]
    LoadBalancer <--> |WSGI| App[Flask App (app.py)]
    
    subgraph "Application Layer"
        App --> Routes[Routes / Blueprints]
        Routes --> |Calls| Service[DatabaseService (services/database.py)]
        Routes --> |Renders| Templates[Jinja2 Templates]
    end
    
    subgraph "Data Layer"
        Service --> |Raw SQL (psycopg2)| DB[(PostgreSQL Database)]
        DB --> |Tables| Tables[Meters, Readings, Invoices, Subscribers]
    end
    
    subgraph "External/Background"
        OSOS[OSOS Metering System] -.-> |Writes Data| DB
    end
```

## 9. Key Insights & Recommendations

### Code Quality & Structure
*   **Pros:** Clean separation of concerns (Routes vs. Services). Comprehensive documentation in `DOCS/`. naming conventions are consistent.
*   **Cons:** `services/database.py` is becoming a "God Class" (1200+ lines). It handles *everything* from dashboard stats to billing logic.

### Recommendations
1.  **Refactor Service Layer:** Split `DatabaseService` into specialized services: `BillingService`, `ReadingService`, `SubscriberService`, `ReportService`. This will improve maintainability.
2.  **Security:** Remove hardcoded credentials from `config.py` immediately. Force use of environment variables.
3.  **ORM Consideration:** While raw SQL is fast, using an ORM (SQLAlchemy) for basic CRUD operations (Users, Subscribers, Settings) would reduce boilerplate code and SQL injection risks, keeping raw SQL only for complex analytical queries.
4.  **API Evolution:** If a mobile app (mentioned in `EFYS_MENU_STRUCTURE.md`) is built, a REST/GraphQL API layer needs to be added.
5.  **Testing:** No tests were found. Adding `pytest` unit tests for the `calculate_invoice` logic is critical before going to production.
