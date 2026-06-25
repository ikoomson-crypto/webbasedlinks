from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here_change_in_production'

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Data files
USERS_FILE = 'users.json'
LINKS_FILE = 'links.json'


# Initialize data files if they don't exist
def init_data_files():
    if not os.path.exists(USERS_FILE):
        # Create default admin user
        default_users = {
            "admin": {
                "id": "admin",
                "username": "admin",
                "password": generate_password_hash("admin123"),
                "role": "admin",
                "created_at": datetime.now().isoformat()
            }
        }
        with open(USERS_FILE, 'w') as f:
            json.dump(default_users, f, indent=2)

    if not os.path.exists(LINKS_FILE):
        default_links = {
            "admin": [
                {"name": "Google", "url": "https://www.google.com", "icon": "🌐", "category": "Search"},
                {"name": "GitHub", "url": "https://github.com", "icon": "🐙", "category": "Development"},
                {"name": "Stack Overflow", "url": "https://stackoverflow.com", "icon": "💡", "category": "Development"},
                {"name": "YouTube", "url": "https://www.youtube.com", "icon": "📺", "category": "Entertainment"},
                {"name": "Reddit", "url": "https://www.reddit.com", "icon": "🔴", "category": "Social"},
                {"name": "LinkedIn", "url": "https://www.linkedin.com", "icon": "💼", "category": "Professional"},
                {"name": "Amazon", "url": "https://www.amazon.com", "icon": "🛒", "category": "Shopping"},
                {"name": "Netflix", "url": "https://www.netflix.com", "icon": "🎬", "category": "Entertainment"},
                {"name": "Wikipedia", "url": "https://www.wikipedia.org", "icon": "📚", "category": "Reference"}
            ]
        }
        with open(LINKS_FILE, 'w') as f:
            json.dump(default_links, f, indent=2)


init_data_files()


# Helper functions
def load_users():
    with open(USERS_FILE, 'r') as f:
        return json.load(f)


def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)


def load_links():
    with open(LINKS_FILE, 'r') as f:
        return json.load(f)


def save_links(links):
    with open(LINKS_FILE, 'w') as f:
        json.dump(links, f, indent=2)


def get_user_links(username):
    links_data = load_links()
    return links_data.get(username, [])


def update_user_links(username, links):
    links_data = load_links()
    links_data[username] = links
    save_links(links_data)


# User class for Flask-Login
class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data['id']
        self.username = user_data['username']
        self.password = user_data['password']
        self.role = user_data.get('role', 'user')
        self.created_at = user_data.get('created_at', datetime.now().isoformat())


@login_manager.user_loader
def load_user(user_id):
    users = load_users()
    if user_id in users:
        return User(users[user_id])
    return None


# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        user_links = get_user_links(current_user.username)
        selected_category = request.args.get('category', 'All')

        if selected_category != 'All':
            filtered_links = [link for link in user_links if link.get('category', 'Uncategorized') == selected_category]
        else:
            filtered_links = user_links

        # Get unique categories for this user
        categories = ['All'] + sorted(set([link.get('category', 'Uncategorized') for link in user_links]))

        return render_template('index.html',
                               links=filtered_links,
                               categories=categories,
                               selected_category=selected_category,
                               username=current_user.username,
                               is_admin=current_user.role == 'admin')
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        users = load_users()
        if username in users:
            user_data = users[username]
            if check_password_hash(user_data['password'], password):
                user = User(user_data)
                login_user(user)
                flash('Logged in successfully!', 'success')

                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('index'))
            else:
                flash('Invalid password.', 'error')
        else:
            flash('User not found.', 'error')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))


@app.route('/admin')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('Admin access required.', 'error')
        return redirect(url_for('index'))

    users = load_users()
    links_data = load_links()

    stats = {
        'total_users': len(users),
        'total_links': sum(len(links) for links in links_data.values()),
        'admin_count': sum(1 for u in users.values() if u.get('role') == 'admin'),
        'user_count': sum(1 for u in users.values() if u.get('role') == 'user')
    }

    return render_template('admin_dashboard.html', stats=stats, users=users)


@app.route('/admin/users')
@login_required
def admin_users():
    if current_user.role != 'admin':
        flash('Admin access required.', 'error')
        return redirect(url_for('index'))

    users = load_users()
    return render_template('admin_users.html', users=users)


@app.route('/admin/users/add', methods=['GET', 'POST'])
@login_required
def admin_add_user():
    if current_user.role != 'admin':
        flash('Admin access required.', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role', 'user')

        users = load_users()
        if username in users:
            flash('Username already exists.', 'error')
            return redirect(url_for('admin_add_user'))

        users[username] = {
            'id': username,
            'username': username,
            'password': generate_password_hash(password),
            'role': role,
            'created_at': datetime.now().isoformat()
        }
        save_users(users)

        # Initialize empty links for new user
        links_data = load_links()
        links_data[username] = []
        save_links(links_data)

        flash(f'User {username} created successfully!', 'success')
        return redirect(url_for('admin_users'))

    return render_template('admin_add_user.html')


@app.route('/admin/users/delete/<username>')
@login_required
def admin_delete_user(username):
    if current_user.role != 'admin':
        flash('Admin access required.', 'error')
        return redirect(url_for('index'))

    if username == 'admin':
        flash('Cannot delete the main admin user.', 'error')
        return redirect(url_for('admin_users'))

    users = load_users()
    if username in users:
        del users[username]
        save_users(users)

        # Remove user's links
        links_data = load_links()
        if username in links_data:
            del links_data[username]
            save_links(links_data)

        flash(f'User {username} deleted successfully.', 'success')

    return redirect(url_for('admin_users'))


@app.route('/admin/links/<username>', methods=['GET', 'POST'])
@login_required
def admin_manage_links(username):
    if current_user.role != 'admin':
        flash('Admin access required.', 'error')
        return redirect(url_for('index'))

    users = load_users()
    if username not in users:
        flash('User not found.', 'error')
        return redirect(url_for('admin_users'))

    user_links = get_user_links(username)

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add':
            name = request.form.get('name')
            url = request.form.get('url')
            category = request.form.get('category', 'Uncategorized')
            icon = request.form.get('icon', '🔗')

            if name and url:
                user_links.append({
                    'name': name,
                    'url': url,
                    'icon': icon,
                    'category': category
                })
                update_user_links(username, user_links)
                flash(f'Link added for {username}!', 'success')

        elif action == 'delete':
            index = int(request.form.get('index'))
            if 0 <= index < len(user_links):
                removed = user_links.pop(index)
                update_user_links(username, user_links)
                flash(f'Removed "{removed["name"]}" from {username}', 'success')

        elif action == 'update':
            index = int(request.form.get('index'))
            if 0 <= index < len(user_links):
                user_links[index]['name'] = request.form.get('name')
                user_links[index]['url'] = request.form.get('url')
                user_links[index]['category'] = request.form.get('category', 'Uncategorized')
                user_links[index]['icon'] = request.form.get('icon', '🔗')
                update_user_links(username, user_links)
                flash(f'Link updated for {username}!', 'success')

        return redirect(url_for('admin_manage_links', username=username))

    return render_template('admin_manage_links.html',
                           username=username,
                           links=user_links)


@app.route('/add_link', methods=['POST'])
@login_required
def add_link():
    name = request.form.get('name')
    url = request.form.get('url')
    category = request.form.get('category', 'Uncategorized')
    icon = request.form.get('icon', '🔗')

    if name and url:
        user_links = get_user_links(current_user.username)
        user_links.append({
            'name': name,
            'url': url,
            'icon': icon,
            'category': category
        })
        update_user_links(current_user.username, user_links)
        flash('Link added successfully!', 'success')

    return redirect(url_for('index'))


@app.route('/remove_link/<int:index>')
@login_required
def remove_link(index):
    user_links = get_user_links(current_user.username)
    if 0 <= index < len(user_links):
        removed = user_links.pop(index)
        update_user_links(current_user.username, user_links)
        flash(f'Removed "{removed["name"]}"', 'success')
    return redirect(url_for('index'))


@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html', username=current_user.username)


@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)