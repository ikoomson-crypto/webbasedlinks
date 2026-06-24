from flask import Flask, render_template, request, redirect, url_for, session
import os
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change this in production

# Sample quick links data
QUICK_LINKS = [
    {"name": "Google", "url": "https://www.google.com", "icon": "🌐", "category": "Search"},
    {"name": "GitHub", "url": "https://github.com", "icon": "🐙", "category": "Development"},
    {"name": "Stack Overflow", "url": "https://stackoverflow.com", "icon": "💡", "category": "Development"},
    {"name": "YouTube", "url": "https://www.youtube.com", "icon": "📺", "category": "Entertainment"},
    {"name": "Reddit", "url": "https://www.reddit.com", "icon": "🔴", "category": "Social"},
    {"name": "Twitter/X", "url": "https://twitter.com", "icon": "🐦", "category": "Social"},
    {"name": "LinkedIn", "url": "https://www.linkedin.com", "icon": "💼", "category": "Professional"},
    {"name": "Amazon", "url": "https://www.amazon.com", "icon": "🛒", "category": "Shopping"},
    {"name": "Netflix", "url": "https://www.netflix.com", "icon": "🎬", "category": "Entertainment"},
    {"name": "Wikipedia", "url": "https://www.wikipedia.org", "icon": "📚", "category": "Reference"},
]

# Additional links for demonstration
CATEGORIES = ["All", "Search", "Development", "Entertainment", "Social", "Professional", "Shopping", "Reference"]

# NEW: Category icons mapping - This fixes the error
CATEGORY_ICONS = {
    "All": "📊",
    "Search": "🌐",
    "Development": "🐙",
    "Entertainment": "📺",
    "Social": "🔴",
    "Professional": "💼",
    "Shopping": "🛒",
    "Reference": "📚",
    "Other": "📌"
}


@app.route('/')
def index():
    """Home page with sidebar and quick links"""
    selected_category = request.args.get('category', 'All')

    # Filter links by category
    if selected_category != 'All':
        filtered_links = [link for link in QUICK_LINKS if link['category'] == selected_category]
    else:
        filtered_links = QUICK_LINKS

    # FIXED: Added category_icons to render_template
    return render_template('index.html',
                           links=filtered_links,
                           categories=CATEGORIES,
                           selected_category=selected_category,
                           category_icons=CATEGORY_ICONS)  # <-- This was missing


@app.route('/add_link', methods=['POST'])
def add_link():
    """Add a new quick link"""
    if request.method == 'POST':
        name = request.form.get('name')
        url = request.form.get('url')
        category = request.form.get('category', 'Other')

        if name and url:
            new_link = {
                "name": name,
                "url": url,
                "icon": "🔗",
                "category": category
            }
            QUICK_LINKS.append(new_link)

            # Update categories if new category
            if category not in CATEGORIES:
                CATEGORIES.append(category)
                CATEGORIES.sort()
                # NEW: Add icon for new category
                if category not in CATEGORY_ICONS:
                    CATEGORY_ICONS[category] = "📌"

    return redirect(url_for('index'))


@app.route('/search')
def search():
    """Search functionality for quick links"""
    query = request.args.get('q', '').lower()
    if query:
        results = [link for link in QUICK_LINKS if query in link['name'].lower() or query in link['category'].lower()]
    else:
        results = QUICK_LINKS

    # FIXED: Added category_icons to render_template
    return render_template('index.html',
                           links=results,
                           categories=CATEGORIES,
                           selected_category='All',
                           search_query=query,
                           category_icons=CATEGORY_ICONS)  # <-- This was missing


@app.route('/remove_link/<int:index>')
def remove_link(index):
    """Remove a quick link by index"""
    if 0 <= index < len(QUICK_LINKS):
        QUICK_LINKS.pop(index)
    return redirect(url_for('index'))


@app.route('/settings')
def settings():
    """Settings page"""
    # FIXED: Added category_icons to render_template
    return render_template('settings.html',
                           categories=CATEGORIES,
                           category_icons=CATEGORY_ICONS)


@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)