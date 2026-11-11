# CipherShield – Role-Based Access Control System for Secure Applications

## Project overview
CipherShield is a cybersecurity mini project that demonstrates Role-Based Access Control (RBAC). Authenticated users receive permissions based on their assigned role.

## Roles and permissions

| Feature | Admin | Manager | User |
|---|---:|---:|---:|
| Login / dashboard | Yes | Yes | Yes |
| View profile | Yes | Yes | Yes |
| View user list | Yes | Yes | No |
| Create manager account | Yes | No | No |
| Access admin panel | Yes | No | No |

## Technologies
- Frontend: HTML, CSS
- Backend: Python Flask
- Database: SQLite
- Authentication: Werkzeug password hashing
- Authorization: Role-based route protection

## Run the project
Install Python 3.9+.

### Windows
```bash
py -m pip install -r requirements.txt
py app.py
```

### Linux / macOS
```bash
python3 -m pip install -r requirements.txt
python3 app.py
```

Open http://127.0.0.1:5000 in your browser.

## Demo login
- Username: `admin`
- Password: `Admin@123`

The application creates this demo admin account automatically on first run. Change the demo password before using the application beyond a classroom demonstration.

## Test the roles
1. Log in as admin and open the Admin panel.
2. Create a manager account.
3. Log out and register a normal user account.
4. Log in as manager: the management page is available, but the admin page is denied.
5. Log in as user: only dashboard and profile are available; direct access to `/manage` and `/admin` is denied.

## Project structure
```text
CipherShield_RBAC/
├── app.py
├── requirements.txt
├── README.md
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── admin.html
│   ├── manage.html
│   ├── profile.html
│   └── denied.html
└── static/
    └── style.css
```

## Security and limitations
Passwords are stored as salted password hashes, not plaintext. SQL queries use parameterized statements. Authorization is enforced on the server for protected routes; hiding a link in the interface is not the security control. This is an educational prototype. Before production use, add CSRF protection, rate limiting, HTTPS, secure cookie settings, audit logging, password reset controls, and deployment hardening. Replace the demo secret key and remove/change the demo administrator credentials.
