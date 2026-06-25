from flask import request, jsonify
import threading
from Debugger import debug


def push_new_event(event_queue, event_type, payload):
    event_queue.put({"event_type": event_type, "data": payload})


def register_route(app, event_queue):
    # Create a route that handles incoming message logic and puts the message in the event queue

    @app.route('/input', methods=['GET', 'POST'])
    def receive_data():
        data = request.get_json()

        debug(data, "EVENT_START")

        if not isinstance(data, dict):
            return jsonify({"status": "error", "message": "Expected JSON object"}), 400

        if 'tile_id' in data and 'tile_type' in data:
            if data.get('tile_type') == 0:
                event_queue.put({"event_type": "tile_removed", "data": {
                    "tile_id": data.get('tile_id'),
                    "tile_type": data.get('tile_type')
                }})
            else:
                event_queue.put({"event_type": "tile_placed", "data": {
                    "tile_id": data.get('tile_id'),
                    "tile_type": data.get('tile_type')
                }})
            return jsonify({"status": "ok"})

        if 'city_location' in data:
            event_queue.put({"event_type": "city_changed", "data": {
                "city_id": data.get('city_location')
            }})
            return jsonify({"status": "ok"})

        if 'time' in data:
            event_queue.put({"event_type": "time_changed", "data": {
                "time": data.get('time')
            }})
            return jsonify({"status": "ok"})

        return jsonify({"status": "error", "message": "Unknown payload shape"}), 400

    return app


def start_flask(app, event_queue):
    register_route(app, event_queue)
    flask_thread = threading.Thread(
        target=lambda: app.run(host='0.0.0.0', port=5000, debug=False),
        daemon=True
    )
    flask_thread.start()



