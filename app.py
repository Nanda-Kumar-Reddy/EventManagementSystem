from flask import Flask, render_template, request, jsonify, redirect, url_for
from sqlite_db import init_db
import sqlite3
from werkzeug.utils import secure_filename
import os, json
import uuid

# init_db()
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max per image
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

SERVICES_FILE = 'services.json'
if not os.path.exists(SERVICES_FILE):
    with open(SERVICES_FILE, 'w') as f:
        json.dump([], f)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/add-service', methods=['POST'])
# def add_service():
#     name = request.form['name']
#     category = request.form['category']
#     # rating = int(request.form['rating'])
#     files = request.files.getlist('images')

#     image_urls = []
#     for file in files:
#         if file and allowed_file(file.filename):
#             filename = secure_filename(file.filename)
#             filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#             file.save(filepath)
#             image_urls.append('/' + filepath)

#     new_service = {
#         "id": str(uuid.uuid4()),
#         "name": name,
#         "category": category,
#         "rating": "",
#         "images": image_urls
#     }

#     with open(SERVICES_FILE, 'r+') as f:
#         services = json.load(f)
#         services.append(new_service)
#         f.seek(0)
#         json.dump(services, f, indent=2)

#     return redirect(url_for('home'))

def add_service():
    name = request.form['name']
    category = request.form['category']
    files = request.files.getlist('images')

    image_urls = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            image_urls.append('/' + filepath)

    conn = sqlite3.connect('eventlink.db')
    c = conn.cursor()
    c.execute('INSERT INTO services (id, name, category, rating, images) VALUES (?, ?, ?, ?, ?)',
              (str(uuid.uuid4()), name, category, None, json.dumps(image_urls)))
    conn.commit()
    conn.close()

    return redirect(url_for('home'))

@app.route('/get-services')
# def get_services():
#     with open(SERVICES_FILE, 'r') as f:
#         return jsonify(json.load(f))
def get_services():
    conn = sqlite3.connect('eventlink.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM services')
    rows = c.fetchall()
    services = []
    for row in rows:
        services.append({
            "id": row["id"],
            "name": row["name"],
            "category": row["category"],
            "rating": row["rating"],
            "images": json.loads(row["images"]) if row["images"] else []
        })
    conn.close()
    return jsonify(services)
@app.route('/book', methods=['POST'])
# def book_service():
#     data = request.json
#     data["status"] = "pending"  # default status
#     with open(BOOKINGS_FILE, 'r+') as f:
#         bookings = json.load(f)
#         bookings.append(data)
#         f.seek(0)
#         json.dump(bookings, f, indent=2)
#     return jsonify({"message": "Booking request sent to provider!"})
def book_service():
    data = request.json
    conn = sqlite3.connect('eventlink.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO bookings (customer_name, event_date, event_time, provider_name, message, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (data["customerName"], data["eventDate"], data["eventTime"], data["providerName"], data["message"], "pending"))
    conn.commit()
    conn.close()
    return jsonify({"message": "Booking request sent to provider!"})

@app.route('/get-bookings')
# def get_bookings():
#     with open(BOOKINGS_FILE, 'r') as f:
#         return jsonify(json.load(f))
def get_bookings():
    conn = sqlite3.connect('eventlink.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM bookings')
    rows = c.fetchall()
    bookings = []
    for row in rows:
        bookings.append({
            "id": row["id"],
            "customerName": row["customer_name"],
            "eventDate": row["event_date"],
            "eventTime": row["event_time"],
            "providerName": row["provider_name"],
            "message": row["message"],
            "status": row["status"]
        })
    conn.close()
    return jsonify(bookings)

@app.route('/update-booking-status', methods=['POST'])
# def update_booking_status():
#     data = request.json  # contains: index, new status
#     with open(BOOKINGS_FILE, 'r+') as f:
#         bookings = json.load(f)
#         bookings[data["index"]]["status"] = data["status"]
#         f.seek(0)
#         f.truncate()
#         json.dump(bookings, f, indent=2)
#     return jsonify({"message": "Booking status updated!"})
def update_booking_status():
    data = request.json  # contains: index, new status
    conn = sqlite3.connect('eventlink.db')
    c = conn.cursor()
    c.execute('UPDATE bookings SET status = ? WHERE id = ?', (data["status"], data["index"]))
    conn.commit()
    conn.close()
    return jsonify({"message": "Booking status updated!"})

@app.route('/rate', methods=['POST'])
# def rate_service():
#     data = request.json  # contains: id, stars

#     print(data)
#     with open(SERVICES_FILE, 'r+') as f:
#         services = json.load(f)
#         found = False
#         for service in services:
#             if service["id"] == data["id"]:
#                 service["rating"] = data["stars"]  # Overwrite with new rating
#                 found = True
#                 break
#         if not found:
#             return jsonify({"message": "Service not found"}), 404

#         f.seek(0)
#         f.truncate()
#         json.dump(services, f, indent=2)

#     return jsonify({"message": f"Thanks for rating {data['stars']} stars!"})
def rate_service():
    data = request.json
    conn = sqlite3.connect('eventlink.db')
    c = conn.cursor()
    c.execute('UPDATE services SET rating = ? WHERE id = ?', (data["stars"], data["id"]))
    conn.commit()
    conn.close()
    return jsonify({"message": f"Thanks for rating {data['stars']} stars!"})

if __name__ == '__main__':
    app.run(debug=True)
