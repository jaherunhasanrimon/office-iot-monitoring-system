"""
Backend entry point.
Starts Flask-SocketIO server and APScheduler simulator.
"""

import os
from dotenv import load_dotenv
load_dotenv()

from app import create_app
from app.realtime import socketio
from app.simulator import start_scheduler

app = create_app()

if __name__ == "__main__":
    scheduler = start_scheduler(app)
    port = int(os.getenv("FLASK_PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"

    try:
        print(f"[Backend] Running on http://localhost:{port}")
        socketio.run(app, host="0.0.0.0", port=port, debug=debug, use_reloader=False)
    finally:
        scheduler.shutdown()
