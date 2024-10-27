import os
from flask import Flask, render_template, request, redirect, url_for
from firebase_admin import credentials, firestore, storage
from firebase import upload_item, search_items
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    matched_items = []
    search_performed = False

    if request.method == 'POST':
        if 'item_image' in request.files:
            # Handle image upload
            file = request.files['item_image']
            bus_stop = request.form.get('bus_stop', '').strip()
            train_station = request.form.get('train_station', '').strip()
            location_type = request.form.get('location_type', '')
            route = request.form.get('route', '')
            category = request.form.get('category', '')

            # Determine the location type
            if bus_stop:
                location_type = 'Bus Stop'
            elif train_station:
                location_type = 'Train Station'

            if file and allowed_file(file.filename) and location_type and route and category:
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)

                # Upload the image, location type, and route to Firebase
                upload_item(file_path, location_type, route, category)
                return redirect(url_for('index'))
        
        # Handle item search
        search_location_type = request.form.get('search_location_type', '')
        search_route = request.form.get('search_route', '').strip()
        search_category = request.form.get('search_category', '')

        if search_location_type and search_route and search_category:
            matched_items = search_items(search_location_type, search_route, search_category)
            search_performed = True

    return render_template('index.html', items=matched_items, search_performed=search_performed)


if __name__ == '__main__':
    app.run(debug=True)
