import os

from app import create_app


application = create_app(os.getenv('APP_SETTINGS', 'production'))
app = application.app

if __name__ == '__main__':
    app.run()
