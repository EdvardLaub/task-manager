#!/usr/bin/env python
import os
from app import app, db

if __name__ == '__main__':
    with app.app_context():
        if os.getenv('FLASK_ENV') == 'production':
            # In production, create tables
            db.create_all()
            print("Database tables created successfully!")
        else:
            # In development, just run the app
            app.run(debug=True)
