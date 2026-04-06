# Changelog

All notable changes to the WriteSpace project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-12-01

### Added

#### Public Landing Page
- Hero section with gradient background and call-to-action buttons for unauthenticated visitors.
- Features section highlighting Easy Writing, Share Globally, and Secure & Reliable.
- Latest posts section displaying the three most recent blog posts.
- Call-to-action section encouraging new user registration.
- Responsive layout with full mobile, tablet, and desktop support.

#### Authentication System
- User registration with display name, username, and password confirmation.
- Case-insensitive username uniqueness validation on registration.
- Login with automatic redirection based on user role (admin to dashboard, regular user to blog list).
- Logout with CSRF-protected POST request and redirect to landing page.
- Login-required protection on all authenticated routes.
- Session-based authentication using Django signed cookie sessions.

#### Role-Based Access Control
- Two user roles: regular User and Admin (staff/superuser).
- Admin users can access the admin dashboard, user management, and edit/delete any blog post.
- Regular users can only edit and delete their own blog posts.
- Staff-only views protected with `user_passes_test` and `is_staff` checks.
- `HttpResponseForbidden` returned for unauthorized access attempts.

#### Blog CRUD Operations
- Create new blog posts with title and content fields.
- Posts automatically assigned to the authenticated author on creation.
- UUID primary keys for all blog posts ensuring unique, non-sequential identifiers.
- Read blog posts in a grid list view with excerpts and author avatars.
- Detailed single post view with full content, author info, and timestamps.
- Edit blog posts with pre-populated form (owner and admin access only).
- Delete blog posts with confirmation prompt (owner and admin access only).
- Posts ordered by creation date descending across all views.
- `select_related('author')` used on all post querysets to prevent N+1 queries.

#### Admin Dashboard
- Overview statistics: total posts, total users, admin count, and regular user count.
- Recent posts list showing the five most recent posts with edit and delete actions.
- Quick action buttons for writing posts, managing users, and viewing all posts.
- Gradient banner header with admin welcome message.
- Staff-only access enforced via `login_required` and `user_passes_test`.

#### User Management
- Admin-only user management page for creating and deleting user accounts.
- Create user form with display name, username, password, and role selection.
- Role selection supporting User and Admin roles with appropriate permission assignment.
- User listing table with avatar, username, role badge, join date, and delete action.
- Protection against deleting superuser accounts with inline error messaging.
- Responsive design with desktop table view and mobile card view.
- Delete confirmation dialog before removing user accounts.

#### Avatar System
- Custom Django template tag `{% avatar user %}` for rendering user avatars.
- Crown emoji (👑) with purple background for admin users.
- Book emoji (📖) with blue background for regular users.
- Consistent avatar display across navbar, blog list, blog detail, and user management.

#### Deployment & Infrastructure
- Vercel deployment configuration with `vercel.json` for Python runtime.
- Cold-start setup in WSGI: automatic `collectstatic`, `migrate`, and `create_default_admin`.
- Custom `create_default_admin` management command for initial superuser provisioning.
- Environment variable configuration via `.env` file with `python-dotenv`.
- `dj-database-url` for flexible database configuration (SQLite default, PostgreSQL supported).
- Gunicorn included for production WSGI serving.

#### Static Files & Styling
- Whitenoise integration for serving static files with compression and caching.
- `CompressedManifestStaticFilesStorage` backend for optimized static file delivery.
- Tailwind CSS via CDN with dark mode support (`class` strategy).
- Custom CSS for scrollbar styling, animations, print styles, and smooth scrolling.
- Responsive design across all pages using Tailwind utility classes and responsive prefixes.
- Custom 404 and 500 error pages with consistent branding.

#### Testing
- Comprehensive test suite using pytest with Django integration.
- Model tests covering UUID generation, field validation, ordering, relationships, and cascade deletes.
- Form tests for LoginForm, RegisterForm, CreateUserForm, and BlogForm validation.
- View tests for all endpoints including authentication, authorization, CRUD, and redirects.
- Test configuration in `pytest.ini` with strict markers and verbose output.

#### Developer Experience
- `.env.example` with documented environment variables and sensible defaults.
- `.gitignore` covering Python, Django, IDE, OS, and build artifacts.
- `requirements.txt` with pinned version ranges for all dependencies.