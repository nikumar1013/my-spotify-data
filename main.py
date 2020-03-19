import json
import requests
import extract
from flask import Flask, request, redirect, g, render_template
from urllib.parse import quote

app = Flask(__name__)

# API Keys
client_id = "26b7856504274aaf8e73196314a11837"
client_secret = "090108ca091346288c6c27e0d0eec073"

# API URLs
auth_url = "https://accounts.spotify.com/authorize"
token_url = "https://accounts.spotify.com/api/token"
base_url = "https://api.spotify.com/v1"

# Redirect uri and authorization scopes
redirect_uri = "http://127.0.0.1:8080/home"
scope = "user-top-read"

# Query parameters for get request
query = {
    "response_type": "code",
    "redirect_uri": redirect_uri,
    "scope": scope,
    "show_dialog": "true",
    "client_id": client_id
}

@app.route("/")
def index():
    # Redirects the user to the Spotify login page (first thing that happens upon app launch)
    url_args = "&".join(["{}={}".format(key, quote(val)) for key, val in query.items()])
    authorization = "{}/?{}".format(auth_url, url_args)
    return redirect(authorization)


@app.route("/home")
def display_top_data():
    # Requests refresh and access tokens (POST)
    auth_token = request.args['code']
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": redirect_uri,
        'client_id': client_id,
        'client_secret': client_secret,
    }
    post_request = requests.post(token_url, data=code_payload)

    # Tokens returned to application
    response_data = json.loads(post_request.text)
    access_token = response_data["access_token"]
    refresh_token = response_data["refresh_token"]
    token_type = response_data["token_type"]
    expires_in = response_data["expires_in"]

    # Use the access token to access Spotify API
    authorization_header = {"Authorization": "Bearer {}".format(access_token)}

    # GET user top artist data
    top_artist_endpoint = "{}/me/top/artists?time_range=long_term&limit=10&offset=0".format(base_url) # NEED TO FIGURE OUT HOW TO PARAMETERIZE THIS
    top_artist_response = requests.get(top_artist_endpoint, headers=authorization_header)
    data = json.loads(top_artist_response.text)
    top_artist_data = extract.get_top_artists(data)

    # GET user top artist data
    top_tracks_endpoint = "{}/me/top/tracks?time_range=long_term&limit=10&offset=0".format(base_url) # NEED TO FIGURE OUT HOW TO PARAMETERIZE THIS
    top_tracks_response = requests.get(top_tracks_endpoint, headers=authorization_header)
    data = json.loads(top_tracks_response.text)
    top_tracks_data = extract.get_top_tracks(data)
    return render_template("index.html", artists=top_artist_data, tracks=top_tracks_data)

# Run the server
if __name__ == "__main__":
    app.run(debug=True, port=8080)
