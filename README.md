# CS50 Web Programming Project 4 — Network

**Network** is a Twitter/X-style social network website that allows users to post updates, follow other users, like posts, and view personalized feed streams.

Built with **Django**, **Bootstrap 5**, **HTML5**, **CSS3**, and **Vanilla JavaScript (ES6+)**.

---

## 📌 Features

- 📝 **All Posts Feed**: View all posts from all users in reverse chronological order with pagination (10 posts per page).
- ✍️ **Create New Post**: Logged-in users can write and submit new posts directly from the home feed.
- 👤 **User Profiles**: View any user's profile, including their follower count, following count, and their complete post timeline.
- 👥 **Follow System**: Toggle follow/unfollow on user profile pages with real-time update.
- 📱 **Following Feed**: Personalized feed showing only posts from users that you follow.
- ✏️ **In-Line Post Editing**: Edit your own posts asynchronously via JavaScript and Fetch API without reloading the page.
- ❤️ **Like / Unlike System**: Toggle post likes asynchronously via JavaScript REST API with keyframe heart animation and live count updates.

---

## 🛠️ Technology Stack

- **Backend Framework**: Python 3.12, Django
- **Frontend**: HTML5, Vanilla JavaScript (ES6+, Fetch API, Async/Await)
- **UI Framework**: Bootstrap 5, Bootstrap Icons, Custom CSS
- **Database**: SQLite3 (Django ORM)

---

## 📂 Folder Structure

```text
/Users/ahmedk.alrashed/Desktop/مشروع ٢/
├── network/                       # Core App Directory
│   ├── migrations/                # Database Migrations
│   ├── static/network/            # Static Assets (styles.css, app.js)
│   ├── templates/network/         # HTML Templates (index, profile, following, login, register)
│   ├── models.py                  # User, Post, Like, Follow Models
│   ├── views.py                   # Views & REST API Endpoints
│   └── urls.py                    # App URL Routing
├── project4/                      # Django Core Project Configuration
├── db.sqlite3                     # SQLite Database
├── manage.py                      # Django CLI Utility
├── seed_data.py                   # Demo Data Seeder Script
└── requirements.txt               # Dependencies
```

---

## 🚀 How to Run

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Apply Migrations**:
   ```bash
   python manage.py migrate
   ```

3. **Seed Demo Data (Optional)**:
   ```bash
   python seed_data.py
   ```

4. **Run Development Server**:
   ```bash
   python manage.py runserver
   ```
   Open `http://127.0.0.1:8000/` in your browser.
