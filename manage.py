#server/manage.py

# from app import create_app
# import sys
# from app.utils.logging import LogColors  # Import LogColors for color coding

# app = create_app()

# if __name__ == "__main__":
#     # Log the host and port information
#     host = app.config['HOST']
#     port = app.config['PORT']
#     app.logger.info(f"{LogColors.BLUE}Server running on http://{host}:{port}{LogColors.RESET}")# Log in blue
    
#     app.run(host=host, port=port, debug=True)


from app import create_app
import sys
from app.utils.logging import LogColors  # Import LogColors for color coding

# Create the app instance here so gunicorn can find it
app = create_app()

if __name__ == "__main__":
    # Log the host and port information
    host = app.config['HOST']
    port = app.config['PORT']
    app.logger.info(f"{LogColors.BLUE}Server running on http://{host}:{port}{LogColors.RESET}")  # Log in blue
    
    app.run(host=host, port=port, debug=True)
