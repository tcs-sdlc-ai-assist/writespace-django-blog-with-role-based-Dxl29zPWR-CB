# ✍️ WriteSpace

A modern blogging platform built with Django where writers connect, share ideas, and inspire others. WriteSpace provides a clean, intuitive interface for creating, managing, and reading blog posts with full admin capabilities.

---

## Features

- **User Authentication** — Register, login, and logout with secure session management
- **Blog Management** — Create, read, edit, and delete blog posts with a distraction-free editor
- **Admin Dashboard** — Overview of platform statistics including total posts, users, and recent activity
- **User Management** — Admin panel for creating, listing, and deleting user accounts with role assignment
- **Role-Based Access Control** — Separate permissions for regular users and administrators
- **Responsive Design** — Fully responsive UI built with Tailwind CSS, optimized for mobile and desktop
- **Dark Mode Support** — Tailwind dark mode utilities throughout all templates
- **Landing Page** — Public-facing homepage showcasing latest posts and platform features
- **UUID Primary Keys** — Blog posts use UUID-based primary keys for secure, non-sequential URLs
- **Serverless Deployment** — Configured for deployment on Vercel with automatic migrations and static file collection

---

## Tech Stack

| Layer        | Technology                          |
|--------------|-------------------------------------|
| Backend      | Python 3.12, Django 5.0+            |
| Database     | SQLite (dev), PostgreSQL (prod)     |
| Styling      | Tailwind CSS (CDN)                  |
| Static Files | WhiteNoise                          |
| Deployment   | Vercel (serverless)                 |
| WSGI Server  | Gunicorn                            |

---

## Project Structure

```
writespace/
├── accounts/                  # User authentication & management app
│   ├── management/
│   │   └── commands/
│   │       └── create_default_admin.py
│   ├── tests/
│   │   ├── test_forms.py
│   │   └── test_views.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── blog/                      # Blog posts app
│   ├── templatetags/
│   │   └── avatar_tags.py
│   ├── tests/
│   │   ├── test_models.py
│   │   └── test_views.py
│   ├── admin.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── static/
│   └── css/
│       └── styles.css
├── templates/
│   ├── accounts/
│   │   ├── landing.html
│   │   ├── login.html
│   │   ├── register.html
│   │   └── user_management.html
│   ├── blog/
│   │   ├── admin_dashboard.html
│   │   ├── blog_detail.html
│   │   ├── blog_form.html
│   │   └── blog_list.html
│   ├── base.html
│   ├── 404.html
│   └── 500.html
├── writespace/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
├── requirements.txt
├── pytest.ini
├── vercel.json
├── .env.example
├── .gitignore
└── README.md
```

---

## Local Development Setup

### Prerequisites

- Python 3.12 or higher
- pip (Python package manager)
- Git

### 1. Clone the Repository

```bash
git clone <repository-url>
cd writespace
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
.venv\Scripts\activate           # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example environment file and update the values as needed:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
SECRET_KEY=your-unique-secret-key
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000,http://127.0.0.1:8000
DEFAULT_ADMIN_USERNAME=admin
DEFAULT_ADMIN_PASSWORD=changeme123
DEFAULT_ADMIN_EMAIL=admin@example.com
```

Generate a secure secret key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 5. Run Database Migrations

```bash
cd writespace
python manage.py migrate
```

### 6. Create the Default Admin User

```bash
python manage.py create_default_admin
```

This creates a superuser using the credentials defined in your `.env` file (`DEFAULT_ADMIN_USERNAME`, `DEFAULT_ADMIN_PASSWORD`, `DEFAULT_ADMIN_EMAIL`).

### 7. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 8. Start the Development Server

```bash
python manage.py runserver
```

Visit [http://localhost:8000](http://localhost:8000) to access the application.

---

## Running Tests

The project uses pytest with the `pytest-django` plugin:

```bash
pip install pytest pytest-django
cd writespace
pytest
```

Run tests with verbose output:

```bash
pytest -v
```

Run a specific test file:

```bash
pytest blog/tests/test_models.py
pytest accounts/tests/test_views.py
```

---

## Deployment on Vercel

### 1. Install the Vercel CLI

```bash
npm install -g vercel
```

### 2. Configure Environment Variables

Set the following environment variables in your Vercel project dashboard (Settings → Environment Variables):

| Variable                  | Required | Description                                      |
|---------------------------|----------|--------------------------------------------------|
| `SECRET_KEY`              | Yes      | Django secret key (generate a unique one)         |
| `DEBUG`                   | Yes      | Set to `False` for production                     |
| `DATABASE_URL`            | Yes      | PostgreSQL connection string                      |
| `ALLOWED_HOSTS`           | Yes      | Comma-separated list of allowed hostnames         |
| `CSRF_TRUSTED_ORIGINS`    | Yes      | Comma-separated list of trusted origins with scheme |
| `DEFAULT_ADMIN_USERNAME`  | No       | Default admin username (defaults to `admin`)      |
| `DEFAULT_ADMIN_PASSWORD`  | No       | Default admin password (defaults to `admin`)      |
| `DEFAULT_ADMIN_EMAIL`     | No       | Default admin email (defaults to `admin@example.com`) |

### 3. Deploy

```bash
vercel --prod
```

The `vercel.json` configuration routes all requests through the Django WSGI application. On cold start, the WSGI module automatically runs `collectstatic`, `migrate`, and `create_default_admin`.

---

## Environment Variables Reference

| Variable                  | Default                                          | Description                                           |
|---------------------------|--------------------------------------------------|-------------------------------------------------------|
| `SECRET_KEY`              | `change-me-to-a-real-secret-key`                 | Django cryptographic signing key                      |
| `DEBUG`                   | `False`                                          | Enable debug mode (`True` or `False`)                 |
| `DATABASE_URL`            | `sqlite:///db.sqlite3`                           | Database connection URL (dj-database-url format)      |
| `ALLOWED_HOSTS`           | `localhost,127.0.0.1`                            | Comma-separated allowed hostnames                     |
| `CSRF_TRUSTED_ORIGINS`    | `http://localhost:8000,http://127.0.0.1:8000`    | Comma-separated trusted origins for CSRF              |
| `DEFAULT_ADMIN_USERNAME`  | `admin`                                          | Username for the default superuser                    |
| `DEFAULT_ADMIN_PASSWORD`  | `changeme123`                                    | Password for the default superuser                    |
| `DEFAULT_ADMIN_EMAIL`     | `admin@example.com`                              | Email for the default superuser                       |

---

## License

This project is **Private**. All rights reserved.