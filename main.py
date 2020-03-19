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

# Query parameters for authorization
auth_query = {
    "response_type": "code",
    "redirect_uri": redirect_uri,
    "scope": scope,
    "show_dialog": "false",
    "client_id": client_id
}


# Returns a token needed to access the Spotify API
def get_access_token():
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
    return access_token


def get_top_artist_data(authorization_header, time_range, limit, offset):
    # GET user top artist data
    top_artist_endpoint = "{}/me/top/artists?time_range={}&limit={}&offset={}".format(base_url, time_range, limit, offset) 
    top_artist_response = requests.get(top_artist_endpoint, headers=authorization_header)
    data = json.loads(top_artist_response.text)
    top_artist_data = extract.get_top_artists(data)
    return top_artist_data


def get_top_tracks_data(authorization_header, time_range, limit, offset):
    # GET user top artist data
    top_tracks_endpoint = "{}/me/top/tracks?time_range={}&limit={}&offset={}".format(base_url, time_range, limit, offset) 
    top_tracks_response = requests.get(top_tracks_endpoint, headers=authorization_header)
    data = json.loads(top_tracks_response.text)
    top_tracks_data = extract.get_top_tracks(data)
    return top_tracks_data


@app.route("/")
def index():
    # Redirects the user to the Spotify login page (first thing that happens upon app launch)
    url_args = "&".join(["{}={}".format(key, quote(val)) for key, val in auth_query.items()])
    authorization = "{}/?{}".format(auth_url, url_args)
    return redirect(authorization)


@app.route("/home")
def display_top_data():
    # Obtain an access token and use it to access the Spotify API
    access_token = get_access_token()
    authorization_header = {"Authorization": "Bearer {}".format(access_token)}

    # Retrieve the top artist data and top tracks data
    top_artist_data = get_top_artist_data(authorization_header, 'long_term', '10', '0')
    top_tracks_data = get_top_tracks_data(authorization_header, 'long_term', '10', '0')

    # Render HTML with the desired data
    return render_template("index.html", artists=top_artist_data, tracks=top_tracks_data)


# @app.route("/top-tracks-by-artist")
# def display_top_tracks_by_artist():
#     # Obtain an access token and use it to access the Spotify API
#     access_token = get_access_token()
#     authorization_header = {"Authorization": "Bearer {}".format(access_token)}

#     return render_template("index.html")

# Run the server
if __name__ == "__main__":
    app.run(debug=True, port=8080)
