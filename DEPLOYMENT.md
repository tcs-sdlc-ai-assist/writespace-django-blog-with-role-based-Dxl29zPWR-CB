# Deployment Guide — WriteSpace on Vercel

This guide walks you through deploying the WriteSpace blog application to **Vercel** with a **Neon PostgreSQL** database.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Neon PostgreSQL Setup](#neon-postgresql-setup)
- [Environment Variables](#environment-variables)
- [Vercel Configuration (`vercel.json`)](#vercel-configuration)
- [WSGI Cold-Start Behavior](#wsgi-cold-start-behavior)
- [Deployment Steps](#deployment-steps)
- [CI/CD Notes](#cicd-notes)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before deploying, ensure you have the following:

1. **Vercel Account** — Sign up at [vercel.com](https://vercel.com) if you don't have one.
2. **Neon PostgreSQL Account** — Sign up at [neon.tech](https://neon.tech) for a serverless PostgreSQL database.
3. **Git Repository** — Your WriteSpace code pushed to GitHub, GitLab, or Bitbucket.
4. **Python 3.12** — The Vercel runtime is configured for Python 3.12 (see `vercel.json`).

---

## Neon PostgreSQL Setup

Neon provides serverless PostgreSQL that pairs well with Vercel's serverless functions.

### 1. Create a Neon Project

1. Log in to [Neon Console](https://console.neon.tech).
2. Click **New Project**.
3. Choose a project name (e.g., `writespace-prod`) and your preferred region.
4. Select PostgreSQL version **15** or **16**.
5. Click **Create Project**.

### 2. Get Your Connection String

After creating the project, Neon displays a connection string. It looks like this:

```
postgres://username:password@ep-example-123456.us-east-2.aws.neon.tech/dbname?sslmode=require
```

Copy this value — you will use it as the `DATABASE_URL` environment variable.

### 3. Connection Pooling (Recommended)

For production workloads, use Neon's **connection pooling** endpoint:

1. In the Neon Console, navigate to your project's **Connection Details**.
2. Toggle **Pooled connection** to get the pooled connection string.
3. The pooled string typically uses port `5432` and includes `-pooler` in the hostname.

Use the pooled connection string as your `DATABASE_URL` for better performance under concurrent serverless invocations.

---

## Environment Variables

Set the following environment variables in your Vercel project settings (**Settings → Environment Variables**):

| Variable | Required | Example | Description |
|---|---|---|---|
| `SECRET_KEY` | **Yes** | `your-random-secret-key` | Django secret key. Generate one with: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `DEBUG` | **Yes** | `False` | **Must be `False` in production.** |
| `DATABASE_URL` | **Yes** | `postgres://user:pass@host/db?sslmode=require` | Neon PostgreSQL connection string. |
| `ALLOWED_HOSTS` | **Yes** | `your-app.vercel.app,your-domain.com` | Comma-separated list of allowed hostnames. Include your Vercel deployment URL and any custom domains. |
| `CSRF_TRUSTED_ORIGINS` | **Yes** | `https://your-app.vercel.app,https://your-domain.com` | Comma-separated list of trusted origins. **Must include the `https://` scheme.** |
| `DEFAULT_ADMIN_USERNAME` | No | `admin` | Username for the auto-created superuser. Defaults to `admin`. |
| `DEFAULT_ADMIN_PASSWORD` | No | `changeme123` | Password for the auto-created superuser. **Change this for production.** |
| `DEFAULT_ADMIN_EMAIL` | No | `admin@example.com` | Email for the auto-created superuser. |

### Important Notes

- **`SECRET_KEY`**: Never reuse the example value. Generate a unique key for every environment.
- **`DEBUG`**: Setting this to `True` in production exposes sensitive information and stack traces.
- **`ALLOWED_HOSTS`**: If you forget to add your Vercel domain, Django returns `400 Bad Request` for every request.
- **`CSRF_TRUSTED_ORIGINS`**: Must include the scheme (`https://`). Without it, all POST requests (login, registration, form submissions) fail with `403 Forbidden`.

---

## Vercel Configuration

The `vercel.json` file at the project root configures how Vercel builds and routes requests:

```json
{
  "builds": [
    {
      "src": "writespace/wsgi.py",
      "use": "@vercel/python",
      "config": {
        "maxLambdaSize": "15mb",
        "runtime": "python3.12"
      }
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "writespace/wsgi.py"
    }
  ]
}
```

### Explanation

| Key | Purpose |
|---|---|
| `builds[0].src` | Entry point for the Python serverless function — the Django WSGI application. |
| `builds[0].use` | Tells Vercel to use the Python runtime builder. |
| `builds[0].config.maxLambdaSize` | Maximum size of the deployed Lambda function (15 MB accommodates Django + dependencies). |
| `builds[0].config.runtime` | Specifies Python 3.12 as the runtime version. |
| `routes[0]` | Catches all incoming requests (`/(.*)`) and forwards them to the WSGI application. |

### How Dependencies Are Installed

Vercel reads `requirements.txt` at the project root and installs all listed packages automatically during the build step. You do **not** need a custom build command.

---

## WSGI Cold-Start Behavior

The `writespace/wsgi.py` file includes cold-start initialization logic that runs automatically when a new serverless function instance spins up:

```python
# Cold-start setup (from wsgi.py):
call_command('collectstatic', '--noinput')
call_command('migrate', '--noinput')
call_command('create_default_admin')
```

### What Happens on Each Cold Start

1. **`collectstatic --noinput`** — Collects static files into the `staticfiles/` directory. WhiteNoise then serves them directly from the Lambda function. This is safe to run repeatedly; it overwrites existing files.

2. **`migrate --noinput`** — Applies any pending database migrations. This is idempotent — if all migrations are already applied, it completes instantly with no changes.

3. **`create_default_admin`** — Runs the custom management command that creates a superuser if one with the configured username does not already exist. If the admin user exists, it skips creation and logs a warning.

### Performance Considerations

- Cold starts add a few seconds to the first request after a period of inactivity.
- Subsequent requests to the same instance are fast (warm invocations).
- Each command is wrapped in a `try/except` block so that a failure in one step (e.g., `collectstatic`) does not prevent the application from starting.
- The `migrate` command acquires a database lock briefly. Under normal conditions this is not an issue, but be aware of it if you have multiple concurrent cold starts.

---

## Deployment Steps

### First-Time Deployment

1. **Push your code** to a Git repository (GitHub, GitLab, or Bitbucket).

2. **Import the project in Vercel**:
   - Go to [vercel.com/new](https://vercel.com/new).
   - Select your repository.
   - Vercel auto-detects the `vercel.json` configuration.

3. **Set environment variables**:
   - Navigate to **Settings → Environment Variables**.
   - Add all required variables from the [Environment Variables](#environment-variables) table above.
   - Apply them to **Production**, **Preview**, and **Development** as needed.

4. **Deploy**:
   - Click **Deploy**.
   - Vercel installs dependencies from `requirements.txt`, builds the function, and deploys.

5. **Verify**:
   - Visit your deployment URL (e.g., `https://your-app.vercel.app`).
   - Log in with the default admin credentials.
   - **Immediately change the default admin password** via the Django admin or user management page.

### Subsequent Deployments

Push to your main branch (or open a pull request for preview deployments). Vercel automatically rebuilds and redeploys.

---

## CI/CD Notes

### Automatic Deployments

- **Production**: Every push to the `main` (or `master`) branch triggers a production deployment.
- **Preview**: Every pull request gets a unique preview deployment URL for testing.

### Running Tests Before Deployment

Add a GitHub Actions workflow (or equivalent) to run tests before merging:

```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python 3.12
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: |
          pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-django

      - name: Run tests
        working-directory: ./writespace
        env:
          SECRET_KEY: test-secret-key-for-ci
          DEBUG: "True"
          DATABASE_URL: sqlite:///db.sqlite3
          ALLOWED_HOSTS: localhost,127.0.0.1
        run: pytest
```

### Branch Protection

For team workflows, enable branch protection on `main`:

- Require pull request reviews before merging.
- Require status checks (tests) to pass before merging.
- This prevents broken code from reaching production.

---

## Troubleshooting

### Static Files Not Loading (404 on CSS/JS)

**Symptoms**: Pages render without styling. Browser console shows 404 errors for `/static/` paths.

**Causes and Fixes**:

1. **`collectstatic` failed silently on cold start.**
   - Check Vercel function logs (**Deployments → Functions → Logs**) for errors during startup.
   - Ensure `STATIC_ROOT` and `STATICFILES_DIRS` are correctly configured in `settings.py` (they are by default).

2. **WhiteNoise not in middleware.**
   - Verify `whitenoise.middleware.WhiteNoiseMiddleware` is listed in `MIDDLEWARE` immediately after `SecurityMiddleware`. This is already configured in the project.

3. **`STATIC_URL` mismatch.**
   - Ensure `STATIC_URL = '/static/'` in settings. Do not change this unless you have a CDN configured.

### Migrations Not Running

**Symptoms**: `ProgrammingError: relation "blog_post" does not exist` or similar database errors.

**Causes and Fixes**:

1. **`DATABASE_URL` not set or incorrect.**
   - Double-check the environment variable in Vercel settings.
   - Ensure the Neon connection string includes `?sslmode=require`.

2. **Neon database is suspended.**
   - Free-tier Neon databases suspend after inactivity. The first connection wakes them up, but it may time out on the initial cold start.
   - Solution: Access the Neon Console to wake the database, then redeploy or wait for the next cold start.

3. **Migration files missing from the repository.**
   - Ensure migration files (`*/migrations/0001_initial.py`, etc.) are committed to Git and not listed in `.gitignore`.
   - Run `python manage.py makemigrations` locally and commit the generated files.

### Default Admin Not Created

**Symptoms**: Cannot log in with the default admin credentials after deployment.

**Causes and Fixes**:

1. **Environment variables not set.**
   - If `DEFAULT_ADMIN_USERNAME` and `DEFAULT_ADMIN_PASSWORD` are not set, the command uses `admin` / `admin` as defaults.

2. **Admin already exists with a different password.**
   - The `create_default_admin` command skips creation if a user with the configured username already exists.
   - To reset: connect to the Neon database directly and update the password, or delete the user and redeploy.

3. **Migrations haven't run yet.**
   - The `create_default_admin` command depends on the `auth_user` table existing. If migrations failed, admin creation also fails.
   - Fix the migration issue first (see above).

### 400 Bad Request

**Symptoms**: Every page returns a `400 Bad Request` error.

**Fix**: Add your Vercel deployment domain to `ALLOWED_HOSTS`:

```
ALLOWED_HOSTS=your-app.vercel.app,your-custom-domain.com
```

### 403 Forbidden on POST Requests

**Symptoms**: Login, registration, and form submissions return `403 Forbidden`.

**Fix**: Add your deployment URL (with `https://` scheme) to `CSRF_TRUSTED_ORIGINS`:

```
CSRF_TRUSTED_ORIGINS=https://your-app.vercel.app,https://your-custom-domain.com
```

### 500 Internal Server Error

**Symptoms**: Application crashes with no useful error message on the page.

**Debugging Steps**:

1. **Check Vercel function logs**: Go to **Deployments → select deployment → Functions tab → View logs**.
2. **Enable `DEBUG` temporarily**: Set `DEBUG=True` in environment variables, redeploy, reproduce the error, then **immediately set it back to `False`**. Never leave `DEBUG=True` in production.
3. **Check database connectivity**: Ensure the Neon database is active and the `DATABASE_URL` is correct.

### Slow Cold Starts

**Symptoms**: First request after inactivity takes 5–15 seconds.

**Explanation**: This is expected behavior for serverless deployments. On cold start, Vercel spins up a new Python process, loads Django, runs `collectstatic`, `migrate`, and `create_default_admin`.

**Mitigations**:

- Keep the Lambda size small (the `maxLambdaSize` of 15 MB is already conservative).
- Use Neon's connection pooling to reduce database connection overhead.
- Vercel Pro/Enterprise plans offer more aggressive keep-alive for functions.
- Consider a cron job or uptime monitor that pings your app periodically to keep instances warm.

### psycopg2 Build Errors

**Symptoms**: Deployment fails with errors related to `psycopg2` compilation.

**Fix**: The project uses `psycopg2-binary` (pre-compiled) in `requirements.txt`, which should work on Vercel without issues. If you see build errors:

1. Ensure `requirements.txt` lists `psycopg2-binary`, **not** `psycopg2`.
2. Clear the Vercel build cache: **Settings → General → Build Cache → Clear**.

---

## Security Checklist for Production

Before going live, verify the following:

- [ ] `SECRET_KEY` is a unique, randomly generated value (not the default from `.env.example`).
- [ ] `DEBUG` is set to `False`.
- [ ] `DEFAULT_ADMIN_PASSWORD` is changed from the default `changeme123`.
- [ ] `ALLOWED_HOSTS` contains only your actual domains.
- [ ] `CSRF_TRUSTED_ORIGINS` contains only your actual domains with `https://`.
- [ ] Neon database credentials are not committed to the repository.
- [ ] `.env` file is listed in `.gitignore` (it is by default).