# app.py (This file will act as the entry point to your application)

from recipe_app import app, db  # Import your Flask app and database instance

if __name__ == '__main__':
    with app.app_context():  # Push an application context
        db.create_all()  # Create database tables if they don't exist
    app.run(debug=True) # Run the application