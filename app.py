from flask import Flask, request, redirect, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
import string
import random

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'  # SQLite database file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define your URL model
class URLMapping(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    short_url = db.Column(db.String(6), unique=True, nullable=False)
    long_url = db.Column(db.String(2000), nullable=False)

    def __repr__(self):
        return f'<URLMapping {self.long_url} -> {self.short_url}>'

# Create the database tables (run this once to initialize the database)
with app.app_context():
 db.create_all()

# Generate short URL function
def generate_short_url():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(6))

# Route to handle URL shortening
@app.route('/', methods=['GET','POST'])
def shorten_url():
    if request.method == 'POST':
        long_url = request.json.get('longurl')
        if long_url:
            short_url = generate_short_url()
            # Save to database
            new_url = URLMapping(short_url=short_url, long_url=long_url)
            db.session.add(new_url)
            db.session.commit()
            return jsonify({'status': 'ok', 'shorturlid': short_url}), 200
        else:
            return jsonify({'status': 'error', 'message': 'No URL provided'}), 400
    return render_template("index.html")

# Route to redirect short URL to long URL
@app.route('/<short_url>')
def redirect_to_long_url(short_url):
    url_mapping = URLMapping.query.filter_by(short_url=short_url).first()
    if url_mapping:
        return redirect(url_mapping.long_url)
    return "URL not found."

# Route to get all short URLs
@app.route('/api/get-all-short-urls/', methods=['GET'])
def get_all_short_urls():
    short_urls = URLMapping.query.all()
    urls = [{'longurl': url.long_url, 'shorturlid': url.short_url, 'count': 0} for url in short_urls]
    return jsonify(urls), 200

if __name__ == '__main__':
    app.run(debug=True)
