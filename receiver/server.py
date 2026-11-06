# Drones for Social Good: the receiver.
#
# What this program does:
#   1. Shows the 3D website (the files in the website folder).
#   2. Shows the team's app page (app.html, next to this file).
#   3. Accepts alert messages ("events") and saves them in data/events.json.
#   4. Tells the app and the website which events exist and how each tank is.
#
# How to run it (Python 3.9 or newer):
#   pip install -r requirements.txt
#   python server.py
#
# There is no password on this server. It is a school demo, so only run it on
# a network you trust.

import json
import os
import tempfile
import threading
import time
import uuid
from datetime import datetime, timedelta, timezone

from flask import Flask, jsonify, request, send_from_directory


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

# Work out every folder from where this file lives. This means the server
# still finds its files if you start it from a different folder.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEBSITE_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "website"))
APP_PAGE = "app.html"
DATA_DIR = os.path.join(BASE_DIR, "data")
DATA_FILE = os.path.join(DATA_DIR, "events.json")
CORRUPT_FILE = os.path.join(DATA_DIR, "events.corrupt.json")

# The only values we accept in an event. Anything else is refused.
TANK_NAMES = ["Tank 1", "Tank 2", "Tank 3"]
ALLOWED_EVENTS = ["WATER_DROP_DETECTED"]
ALLOWED_SEVERITIES = ["error", "warning", "ok"]
ALLOWED_SOURCES = ["simulator", "real_sensor"]

# The fields an event must have. Any other field that is sent gets ignored.
REQUIRED_FIELDS = [
    "device",
    "esp_board",
    "tank",
    "event",
    "severity",
    "source",
    "timestamp",
]

MAX_NAME_LENGTH = 64         # Longest allowed device or ESP board name.
MAX_BODY_BYTES = 16 * 1024   # Biggest message we accept: 16 KB.
MAX_EVENTS_RETURNED = 100    # How many events /api/events sends back.
MAX_EVENTS_STORED = 1000     # Above this, old cleared events get removed.
STATUS_WINDOW_MINUTES = 15   # "Recent" means within this many minutes.
REPLACE_ATTEMPTS = 5         # How many times to retry swapping in a new file.
DEFAULT_PORT = 5000


# ---------------------------------------------------------------------------
# Create the web app
# ---------------------------------------------------------------------------

# static_folder and static_url_path="" tell Flask that a request such as
# /styles.css should be answered with the file website/styles.css.
app = Flask(__name__, static_folder=WEBSITE_DIR, static_url_path="")

# Refuse any message bigger than the limit above.
app.config["MAX_CONTENT_LENGTH"] = MAX_BODY_BYTES

# Tell browsers to check for new files each time, so edits show up right away.
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

# The server can handle several requests at the same moment. This lock makes
# them take turns with the data file, so two requests cannot overwrite each
# other's changes. Reads take a turn too: on Windows, a file cannot be swapped
# for a new one while another request still has it open.
events_lock = threading.Lock()


# ---------------------------------------------------------------------------
# Time helpers
# ---------------------------------------------------------------------------

def utc_now_iso():
    """Return the current time, in UTC, as ISO 8601 text."""
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def parse_iso_time(text):
    """Turn ISO 8601 text into a datetime. Return None if it is not valid."""
    if not isinstance(text, str):
        return None

    # Browsers write UTC time with a "Z" on the end. Older Python versions do
    # not understand the "Z", so we swap it for the same thing written "+00:00".
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"

    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None

    # A time with no time zone cannot be compared with one that has a zone,
    # so we treat it as UTC.
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


# ---------------------------------------------------------------------------
# Reading and writing data/events.json
#
# Call these two functions only while holding events_lock.
# ---------------------------------------------------------------------------

def choose_corrupt_backup_path():
    """Pick a backup name that will not overwrite an earlier backup."""
    if not os.path.exists(CORRUPT_FILE):
        return CORRUPT_FILE

    # This time has no colons, because Windows does not allow them in file names.
    time_text = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    return os.path.join(DATA_DIR, "events.corrupt-" + time_text + ".json")


def back_up_corrupt_file():
    """Move a damaged data file out of the way and return an empty list.

    If the file cannot be moved, the error is passed up. The damaged file then
    stays where it is, because the next save would otherwise overwrite it and
    lose every earlier alert. The server replies with an error until a later
    try at the backup works.
    """
    print("WARNING: data/events.json could not be understood.")
    backup_path = choose_corrupt_backup_path()
    try:
        os.replace(DATA_FILE, backup_path)
    except OSError as error:
        print("It could not be backed up, so it has been left in place:", error)
        raise
    print("It was saved as data/" + os.path.basename(backup_path) + ". Starting with no events.")
    return []


def is_event_list(data):
    """Check that the data is a list of events that each have a text id."""
    if not isinstance(data, list):
        return False
    for item in data:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            return False
    return True


def load_events():
    """Read all events from the file, oldest first.

    A missing, empty or damaged file gives an empty list, so it cannot crash
    the server. Any other read problem (such as the file being locked for a
    moment, or a damaged file that cannot be backed up) is passed up as an
    error instead. Pretending the list was empty could make the next save wipe
    out real alerts. The error handler further down turns it into a clear reply.
    """
    try:
        # "utf-8-sig" also copes with the invisible mark some Windows editors
        # put at the start of a file.
        with open(DATA_FILE, "r", encoding="utf-8-sig") as data_file:
            text = data_file.read()
    except FileNotFoundError:
        return []
    except UnicodeDecodeError:
        return back_up_corrupt_file()

    if not text.strip():
        return []

    try:
        events = json.loads(text)
    except (ValueError, RecursionError):
        return back_up_corrupt_file()

    if not is_event_list(events):
        return back_up_corrupt_file()

    return events


def replace_file(source, target):
    """Swap the new file into place, trying again if it is briefly locked.

    On Windows, antivirus or backup programs can hold a file for a moment.
    """
    for attempt in range(REPLACE_ATTEMPTS):
        try:
            os.replace(source, target)
            return
        except PermissionError:
            if attempt == REPLACE_ATTEMPTS - 1:
                raise
            time.sleep(0.1)


def save_events(events):
    """Save all events safely.

    We write to a temporary file first and then swap it into place in one
    step. If the power fails halfway through, the old file is still complete.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    handle, temp_path = tempfile.mkstemp(dir=DATA_DIR, prefix="events-", suffix=".tmp")
    try:
        with os.fdopen(handle, "w", encoding="utf-8") as temp_file:
            json.dump(events, temp_file, indent=2)
            temp_file.flush()
            os.fsync(temp_file.fileno())
        replace_file(temp_path, DATA_FILE)
    except Exception:
        # Tidy up the temporary file, then report the original problem.
        try:
            os.remove(temp_path)
        except OSError:
            pass
        raise


def trim_events(events):
    """Keep the file from growing forever by removing the oldest CLEARED events.

    Only cleared events are ever removed, so an alert nobody has dealt with
    can never quietly disappear. This means the list can stay above the limit
    if nobody clears anything, and that is on purpose.
    """
    extra = len(events) - MAX_EVENTS_STORED
    if extra <= 0:
        return events

    kept = []
    for event in events:   # The list is oldest first.
        if extra > 0 and event.get("cleared"):
            extra -= 1     # Skip this one, so it is not kept.
        else:
            kept.append(event)
    return kept


# ---------------------------------------------------------------------------
# Checking an incoming event
# ---------------------------------------------------------------------------

def validate_event(body):
    """Check an incoming event.

    Returns (clean_event, None) when it is valid, or (None, problem_text) when
    it is not. clean_event holds only the fields we know about.
    """
    if not isinstance(body, dict):
        return None, "Please send a JSON object, with the Content-Type application/json."

    for field in REQUIRED_FIELDS:
        if not isinstance(body.get(field), str):
            return None, "The field '" + field + "' is missing or is not text."

    for field in ("device", "esp_board"):
        value = body[field]
        if not value.strip() or len(value) > MAX_NAME_LENGTH:
            return None, "The field '" + field + "' must be 1 to 64 characters long."

    if body["tank"] not in TANK_NAMES:
        return None, "The field 'tank' must be Tank 1, Tank 2 or Tank 3."
    if body["event"] not in ALLOWED_EVENTS:
        return None, "The field 'event' must be WATER_DROP_DETECTED."
    if body["severity"] not in ALLOWED_SEVERITIES:
        return None, "The field 'severity' must be error, warning or ok."
    if body["source"] not in ALLOWED_SOURCES:
        return None, "The field 'source' must be simulator or real_sensor."
    if parse_iso_time(body["timestamp"]) is None:
        return None, "The field 'timestamp' must be a date and time in ISO 8601 format."

    clean_event = {}
    for field in REQUIRED_FIELDS:
        clean_event[field] = body[field]
    return clean_event, None


# ---------------------------------------------------------------------------
# Small helpers for events
# ---------------------------------------------------------------------------

def is_uncleared_error(event):
    """True if this event is an error that nobody has cleared yet."""
    return event.get("severity") == "error" and not event.get("cleared")


def is_recent(event, cutoff):
    """True if the server received this event at or after the cutoff time."""
    received_at = parse_iso_time(event.get("server_timestamp"))
    return received_at is not None and received_at >= cutoff


def find_event(events, event_id):
    """Return the event with this id, or None if there is no such event."""
    for event in events:
        if event.get("id") == event_id:
            return event
    return None


def mark_acknowledged(event, now):
    """Record that someone has seen this event. Keeps the first time it happened."""
    if not event.get("acknowledged"):
        event["acknowledged"] = True
        event["acknowledged_at"] = now


def mark_cleared(event, now):
    """Record that this event has been dealt with. Clearing also acknowledges."""
    mark_acknowledged(event, now)
    if not event.get("cleared"):
        event["cleared"] = True
        event["cleared_at"] = now


def not_found_reply():
    """The answer we give when an event id does not exist."""
    return jsonify({"ok": False, "error": "No event with that id was found."}), 404


def build_tank_status(tank, events, cutoff):
    """Work out the status of one tank.

    The rules:
    - Error: the tank has at least one uncleared event with severity "error".
      This stays true however old the event is, because a leak must not
      silently disappear just because 15 minutes went by. "acknowledged" is
      true only if ALL of the tank's uncleared errors have been acknowledged.
    - OK: no uncleared errors, and at least one event in the last 15 minutes
      (going by the time the server received it).
    - No data: no uncleared errors, and no event in the last 15 minutes.

    device, source and last_event_at come from the newest event for this tank,
    whatever state that event is in.
    """
    tank_events = [event for event in events if event.get("tank") == tank]
    open_errors = [event for event in tank_events if is_uncleared_error(event)]
    newest = tank_events[-1] if tank_events else None   # The list is oldest first.

    if open_errors:
        status = "Error"
    elif any(is_recent(event, cutoff) for event in tank_events):
        status = "OK"
    else:
        status = "No data"

    return {
        "tank": tank,
        "status": status,
        "device": newest.get("device") if newest else None,
        "source": newest.get("source") if newest else None,
        "last_event_at": newest.get("server_timestamp") if newest else None,
        "acknowledged": bool(open_errors) and all(
            event.get("acknowledged") for event in open_errors
        ),
    }


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

@app.route("/")
def website_home():
    """Show the 3D website. Its other files are served by the static_folder."""
    return send_from_directory(WEBSITE_DIR, "index.html")


@app.route("/app")
def app_page():
    """Show the app page that the team uses on a phone or laptop."""
    return send_from_directory(BASE_DIR, APP_PAGE)


# ---------------------------------------------------------------------------
# Receiving events
# ---------------------------------------------------------------------------

@app.route("/events", methods=["POST"])
def receive_event():
    """Check a new event, add the server's own details, and save it."""
    try:
        body = request.get_json(silent=True)
    except RecursionError:
        # A message nested too many levels deep cannot be read.
        body = None

    clean_event, problem = validate_event(body)
    if problem:
        return jsonify({"ok": False, "error": problem}), 400

    stored_event = dict(clean_event)
    stored_event["id"] = uuid.uuid4().hex
    stored_event["server_timestamp"] = utc_now_iso()
    stored_event["acknowledged"] = False
    stored_event["acknowledged_at"] = None
    stored_event["cleared"] = False
    stored_event["cleared_at"] = None

    with events_lock:
        events = load_events()
        events.append(stored_event)
        save_events(trim_events(events))

    return jsonify({"ok": True})


# ---------------------------------------------------------------------------
# Reading events and tank status
# ---------------------------------------------------------------------------

@app.route("/api/events")
def list_events():
    """Send back the newest events, newest first."""
    with events_lock:
        events = load_events()

    # New events are always added to the end of the list, so the end of the
    # list is the newest. We take the last ones and flip the order.
    newest_first = events[-MAX_EVENTS_RETURNED:][::-1]
    return jsonify({"events": newest_first})


@app.route("/api/status")
def tank_status():
    """Send back the status of each tank. See build_tank_status for the rules."""
    with events_lock:
        events = load_events()

    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(minutes=STATUS_WINDOW_MINUTES)
    tanks = [build_tank_status(tank, events, cutoff) for tank in TANK_NAMES]

    return jsonify({
        "window_minutes": STATUS_WINDOW_MINUTES,
        "generated_at": now.isoformat(timespec="milliseconds"),
        "tanks": tanks,
    })


# ---------------------------------------------------------------------------
# Acknowledge and Clear buttons
# ---------------------------------------------------------------------------

@app.route("/api/events/<event_id>/acknowledge", methods=["POST"])
def acknowledge_event(event_id):
    """Mark one event as seen."""
    with events_lock:
        events = load_events()
        event = find_event(events, event_id)
        if event is None:
            return not_found_reply()
        mark_acknowledged(event, utc_now_iso())
        save_events(events)
    return jsonify({"ok": True})


@app.route("/api/events/<event_id>/clear", methods=["POST"])
def clear_event(event_id):
    """Mark one event as dealt with. It stays in the history."""
    with events_lock:
        events = load_events()
        event = find_event(events, event_id)
        if event is None:
            return not_found_reply()
        mark_cleared(event, utc_now_iso())
        save_events(trim_events(events))
    return jsonify({"ok": True})


@app.route("/api/acknowledge-all", methods=["POST"])
def acknowledge_all():
    """Mark every uncleared error as seen."""
    with events_lock:
        events = load_events()
        now = utc_now_iso()
        for event in events:
            if is_uncleared_error(event):
                mark_acknowledged(event, now)
        save_events(events)
    return jsonify({"ok": True})


@app.route("/api/clear-all", methods=["POST"])
def clear_all():
    """Mark every uncleared error as dealt with. They stay in the history."""
    with events_lock:
        events = load_events()
        now = utc_now_iso()
        for event in events:
            if is_uncleared_error(event):
                mark_cleared(event, now)
        save_events(trim_events(events))
    return jsonify({"ok": True})


# ---------------------------------------------------------------------------
# Friendly error replies
# ---------------------------------------------------------------------------

@app.errorhandler(413)
def message_too_big(error):
    """The message was over the 16 KB limit."""
    return jsonify({"ok": False, "error": "That message is too big. The limit is 16 KB."}), 413


@app.errorhandler(OSError)
def storage_problem(error):
    """The data file could not be read or written, so we say so honestly."""
    print("ERROR: problem with the data file:", error)
    message = "The receiver could not read or save its data file. Please try again."
    return jsonify({"ok": False, "error": message}), 500


# ---------------------------------------------------------------------------
# Starting the server
# ---------------------------------------------------------------------------

def get_port():
    """Use the PORT setting if there is a valid one, otherwise port 5000."""
    text = os.environ.get("PORT", str(DEFAULT_PORT))
    try:
        return int(text)
    except ValueError:
        print("PORT is not a number, so using port", DEFAULT_PORT)
        return DEFAULT_PORT


def main():
    """Check the data file, print some help, and start the server."""
    port = get_port()

    # Reading the file now means a damaged file gets reported at start-up.
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with events_lock:
            load_events()
    except OSError as error:
        print("WARNING: could not open the data file:", error)

    print("")
    print("Drones for Social Good receiver")
    print("-------------------------------")
    print("On this laptop:")
    print("  Website: http://localhost:" + str(port) + "/")
    print("  App:     http://localhost:" + str(port) + "/app")
    print("On a phone or another laptop on the same Wi-Fi:")
    print("  Website: http://[Laptop IP]:" + str(port) + "/")
    print("  App:     http://[Laptop IP]:" + str(port) + "/app")
    print("Remember to replace [Laptop IP] with this laptop's address.")
    print("On Windows, type ipconfig in PowerShell and look for the IPv4 Address.")
    print("Press Ctrl+C to stop the server.")
    print("")

    # 0.0.0.0 means "accept connections from other devices on the network too".
    app.run(host="0.0.0.0", port=port, debug=False)


# This part only runs when you start this file directly.
if __name__ == "__main__":
    main()
