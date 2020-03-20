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
scope = "user-top-read user-read-recently-played"

# Query parameters for authorization
auth_query = {
    "response_type": "code",
    "redirect_uri": redirect_uri,
    "scope": scope,
    "show_dialog": "false",
    "client_id": client_id
}

# Returns a token needed to access the Spotify API
def generate_access_token():
    global access_token
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

# Gets the name of a track or artist from its respective Spotify id
def convert_id_to_name(auth_header, datatype, spot_id):
    endpoint = "{}/{}/{}".format(base_url, datatype, spot_id)
    response = requests.get(endpoint, headers=auth_header)
    data = json.loads(response.text)
    name = data['name']
    return name

# GET a user's top artists
def get_top_artist_data(auth_header, time_range, limit, offset, tag):
    endpoint = "{}/me/top/artists?time_range={}&limit={}&offset={}".format(base_url, time_range, limit, offset) 
    response = requests.get(endpoint, headers=auth_header)
    data = json.loads(response.text)
    top_artist_data = extract.get_top_artists(data, tag)
    return top_artist_data

# GET a user's top tracks
def get_top_tracks_data(auth_header, time_range, limit, offset, tag):
    endpoint = "{}/me/top/tracks?time_range={}&limit={}&offset={}".format(base_url, time_range, limit, offset) 
    response = requests.get(endpoint, headers=auth_header)
    data = json.loads(response.text)
    top_tracks_data = extract.get_top_tracks(data, tag)
    return top_tracks_data

# GET a user's top tracks grouped by their top artists
def get_top_tracks_by_artist(auth_header):
    top_tracks = get_top_tracks_data(auth_header, 'long_term', '50', '0', 'name')
    top_artists = get_top_artist_data(auth_header, 'long_term', '10', '0', 'name')
    result = extract.get_top_tracks_by_artist(top_tracks, top_artists)
    return result

def get_recent_tracks_data(auth_header, limit, tag):
    endpoint = "{}/me/player/recently-played?type={}&limit={}&after={}".format(base_url,'track', limit, '0')
    response = requests.get(endpoint, headers=auth_header)
    data = json.loads(response.text)
    recent_tracks_data = extract.get_recent_tracks(data, tag)
    return recent_tracks_data

# Initial route for user authentication with Spotify
@app.route("/")
def index():
    # Redirects the user to the Spotify login page (first thing that happens upon app launch)
    url_args = "&".join(["{}={}".format(key, quote(val)) for key, val in auth_query.items()])
    authorization = "{}/?{}".format(auth_url, url_args)
    return redirect(authorization)


# Homepage of application
@app.route("/home")
def display_top_data():
    # Generate a token with which to access the Spotify API
    generate_access_token()
    auth_header = {"Authorization": "Bearer {}".format(access_token)}

    # Retrieve the top artist data and top tracks data
    top_artist_data = get_top_artist_data(auth_header, 'long_term', '10', '0', 'name')
    top_tracks_data = get_top_tracks_data(auth_header, 'long_term', '10', '0', 'name')
    recent_tracks_data = get_recent_tracks_data(auth_header, '10', 'name')

    # # Convert every artist id in the list to an artist name
    # for i in range(len(top_artist_data)):
    #     artist_id = top_artist_data[i]
    #     artist_name = convert_id_to_name(auth_header, 'artists', artist_id)
    #     top_artist_data[i] = artist_name

    # # Convert every id in the dictionary to a name
    # temp = {}
    # for track_id in top_tracks_data:
    #     artist_id = top_tracks_data.get(track_id)
    #     track_name = convert_id_to_name(auth_header, 'tracks', track_id)
    #     artist_name = convert_id_to_name(auth_header, 'artists', artist_id)
    #     temp[track_name] = artist_name
    # top_tracks_data = temp

    # Render HTML with the desired data
    return render_template("index.html", artists=top_artist_data, tracks=top_tracks_data,recent=recent_tracks_data)



# Page for viewing top tracks grouped by artist
@app.route("/top-tracks-by-artist")
def display_top_tracks_by_artist():
    # Obtain an access token and use it to access the Spotify API
    auth_header = {"Authorization": "Bearer {}".format(access_token)}
    top_tracks_by_artist_data = get_top_tracks_by_artist(auth_header)
    
    # # Convert every id in the dictionary to a name
    # temp_dict = {}
    # for artist_id in top_tracks_by_artist_data:
    #     temp_list = []
    #     track_id_list = top_tracks_by_artist_data.get(artist_id)
    #     for track_id in track_id_list:
    #         track_name = convert_id_to_name(auth_header, 'tracks', track_id)
    #         temp_list.append(track_name)
    #     artist_name = convert_id_to_name(auth_header, 'artists', artist_id)
    #     temp_dict[artist_name] = temp_list
    # top_tracks_by_artist_data = temp_dict

    # Render HTML with the desired data
    return render_template("tracks.html", content=top_tracks_by_artist_data)


# Run the server
if __name__ == "__main__":
    app.run(debug=True, port=8080)
