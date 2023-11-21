"""
(C) whsmith 2023 All Rights Reserved.
This code may not be used, copied, distributed, or reproduced in part or in whole
for commercial or personal purposes without the express written consent of the owner.
"""

# Import necessary libraries
import json
import os
from datetime import datetime

import pytz
import spotipy
from flask import (
    Flask,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_restful import Api, Resource
from pytube import YouTube
from spotipy.oauth2 import SpotifyClientCredentials
from youtubesearchpython import VideosSearch
from dotenv import load_dotenv
from flask_session import Session

# Import custom modules
from platform_detect import reg_b, reg_v
from redirect_config import redirects

# Load the local .env file into the environment
load_dotenv()

# Global Config
ADMIN_USERNAME = os.getenv("admin_username")
ADMIN_PASSWORD = os.getenv("admin_password")
REDIRECT_MOBILE = os.getenv("redirect_mobile").lower() in ["on", "yes", "true"]
MOBILE_VERSION_URL = os.getenv("mobile_version_url")

# Initialize Spotify API client
sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=os.getenv("spotify_client_id"),
        client_secret=os.getenv("spotify_client_secret"),
    )
)

# Create Flask application
app = Flask(__name__)
api = Api(app)

# Flask Configuration
flask_config = {
    "CACHE": True,  # Set flask asset caching to True
    "SECRET_KEY": os.urandom(24),  # Flask secret key for encryption
    "SESSION_TYPE": "filesystem",  # Flask Session local session data config
}
app.config.from_mapping(flask_config)

# Flask Extensions
Session(app)


# Helper function to detect mobile browsers
def detect_mobile_browser(req):
    user_agent = req.headers.get("User-Agent")
    if user_agent:
        b = reg_b.search(user_agent)
        v = reg_v.search(user_agent[0:4])
        if b or v:
            return True
    return False


# Route Helpers


def serve_default_template(template: str, request):
    if detect_mobile_browser(request) and REDIRECT_MOBILE:
        return redirect(MOBILE_VERSION_URL)

    # Load data from a JSON file
    with open("static/custom_content/song_of_the_week.json") as f:
        song_of_the_week = json.load(f)

    return render_template(
        template,
        song_of_the_week=song_of_the_week,
        signed_in=session.get("admin") if True else False,
    )


# Define Routes


@app.route("/", methods=["GET"])
def _home():
    return serve_default_template("home.html", request)


@app.route("/work", methods=["GET"])
def _work():
    return serve_default_template("work.html", request)


@app.route("/socials", methods=["GET"])
def _socials():
    return serve_default_template("socials.html", request)


@app.route("/admin", methods=["GET", "POST"])
def _admin():
    # Check if the user is using a mobile browser
    if detect_mobile_browser(request) and REDIRECT_MOBILE:
        return redirect("https://m.whsmith.me?redirect=from_desktop")

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin"] = True
            print("success")
            return redirect("/admin")
        else:
            print("Wrong")
            for i in request.form.items():
                print(i)
            return render_template(
                "login.html", error="Incorrect Username and or Password."
            )

    if session.get("admin"):
        desired_timezone = "Europe/London"

        current_time = datetime.now(pytz.timezone(desired_timezone))
        greeting = (
            "Good morning"
            if current_time.hour < 12
            else "Good afternoon"
            if current_time.hour < 17
            else "Good evening"
        )

        return render_template(
            "admin.html",
            signed_in=session.get("admin") if True else False,
            greeting=greeting,
            username=ADMIN_USERNAME.capitalize(),
        )
    else:
        return render_template("login.html")


@app.route("/redirect/<name>")
def _redirect(name):
    for entry in redirects:
        if entry["name"] == name:
            # Log the redirect details
            with open("redirects_log.json") as f:
                redirects_log = json.load(f)

            redirects_log.append(
                {
                    "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "ip": request.remote_addr,
                    "user_agent": request.headers.get("User-Agent", default=None),
                    "redirect": name,
                }
            )

            with open("redirects_log.json", "w+") as f:
                json.dump(redirects_log, f, indent=4)

            return redirect(entry["redirects_to"])
    return "404 - Redirect not found", 404


# Define API resources


# Song of the week static resources and statistics
class SongOfTheWeek(Resource):
    def get(self):
        with open("static/custom_content/song_of_the_week.json") as f:
            song_of_the_week = json.load(f)
        return jsonify(song_of_the_week)

    def post(self):
        with open("static/custom_content/song_of_the_week_stats.json") as f:
            song_of_the_week_stats = json.load(f)

        song_of_the_week_stats["plays"] += 1

        with open("static/custom_content/song_of_the_week_stats.json", "w+") as f:
            json.dump(song_of_the_week_stats, f)


# Song of the week updating logic
class ManageSongOfTheWeek(Resource):
    def put(self):
        if not session.get("admin"):
            return make_response(
                jsonify(
                    {
                        "ok": False,
                        "error": "403 Forbidden - Not authorized to manage song of the week, please log in.",
                    }
                ),
                403,
            )

        song_url = request.args.get("song_url")
        if (
            "https://www.youtube.com/watch?v=" not in song_url
            and "https://open.spotify.com/track/" not in song_url
            and "https://youtube.com/watch?v=" not in song_url
        ):
            return make_response(
                jsonify(
                    {
                        "ok": False,
                        "error": "Invalid 'song_url' parameter",
                        "song_url": song_url,
                    }
                ),
                400,
            )
        else:
            if "https://open.spotify.com/track/" in song_url:
                spotify = True
            else:
                spotify = False

        if spotify:
            json_data = json.loads(json.dumps(sp.track(song_url)))
            query = f'{json_data["name"]} - {json_data["artists"][0]["name"]}'

            search = VideosSearch(query, limit=1)

            url = (
                f"https://www.youtube.com/watch?v={search.result()['result'][0]['id']}"
            )

        else:
            url = song_url

        yt = YouTube(url)

        s = yt.streams.filter(only_audio=True).first()
        s.download(
            output_path="static/custom_content",
            filename="song_of_the_week.mp3",
            max_retries=3,
        )

        song_of_the_week_data_path = os.path.join(
            "static", "custom_content", "song_of_the_week.json"
        )

        song_of_the_week_data = {
            "track_name": json_data["name"],
            "track_artists": "".join(
                artist["name"] + " " for artist in json_data["artists"]
            ),
            "url": song_url,
            "avalible_at": "/static/custom_content/song_of_the_week.mp3",
        }

        with open(song_of_the_week_data_path, "w+") as f:
            json.dump(song_of_the_week_data, f)

        return make_response(
            jsonify({"ok": True, "message": "Song of the Week updated successfully."}),
            201,
        )


# Add API resources to the API
api.add_resource(SongOfTheWeek, "/api/v1/song_of_the_week")
api.add_resource(ManageSongOfTheWeek, "/api/v1/song_of_the_week/")

# Run the Flask application
if __name__ == "__main__":
    app.run(port=5000, debug=True)
