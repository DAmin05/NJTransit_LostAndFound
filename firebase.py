import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import firebase_admin
from firebase_admin import credentials, firestore, storage

# Initialize Firebase Admin SDK
cred = credentials.Certificate("lost-found.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'lost-found-83655.appspot.com'
})

db = firestore.client()
bucket = storage.bucket()

VALID_CATEGORIES = [
    "Art/Photos", "Baby Items", "Bag", "Books/Writing Instruments", 
    "Cell Phones", "Clothing", "Electronics/Accessories", 
    "Household Goods/Appliances", "ID Cards", "Wallets", "Jewelry", 
    "Medical Field Related", "Misc", "None", "Perishable", 
    "Personal Accessories", "Shoes", "Sports/Recreation", "Tickets", "Toys"
]

def upload_item(image_path, location_type, route, category):
    """Upload image, location, and route to Firebase Storage and Firestore under a specific category."""
    if category not in VALID_CATEGORIES:
        print(f"Invalid category: {category}")
        return

    try:
        item_id = db.collection(category).document().id

        # Upload image to Firebase Storage
        blob = bucket.blob(f"{category}/{item_id}.jpg")
        with open(image_path, 'rb') as image_file:
            blob.upload_from_file(image_file)

        # Make the image publicly accessible
        blob.make_public()

        # Use the public URL
        image_url = blob.public_url

        # Store item metadata in Firestore
        item_data = {
            'item_id': item_id,
            'location_type': location_type,  # New variable to store "Bus Stop" or "Train Station"
            'route': route,                  # New variable to store bus number or train route
            'image_url': image_url,
            'category': category
        }
        db.collection(category).document(item_id).set(item_data)

        print(f"Uploaded item in category '{category}': {location_type}, Route: {route}, Image URL: {image_url}")
        
        os.remove(image_path)
    except Exception as e:
        print(f"Error uploading item: {e}")


def search_items(location_type, route, category):
    """Search for matching items in Firestore within a specified category, location type, and route."""
    try:
        items_ref = db.collection(category)
        matches = items_ref.stream()

        matched_items = []
        for item in matches:
            item_data = item.to_dict()
            item_location_type = item_data.get('location_type', '')
            item_route = item_data.get('route', '')

            # Debugging output for each item
            print(f"Checking item in category '{category}': Location: {item_location_type}, Route: {item_route}")
            
            # Check for matching location and route
            if location_type.lower() == item_location_type.lower() and route.lower() == item_route.lower():
                print(f"Match found: {item_data}")
                matched_items.append(item_data)

        # Final debug output
        print(f"Total matched items in category '{category}': {matched_items}")
        return matched_items
    except Exception as e:
        print(f"Error searching items: {e}")
        return []
