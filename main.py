# Authors: Nikhil Kumar, Abhijit Raman, Nicholas Wille
import json
import requests
import extract
import os
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import pickle
from flask import Flask, request, redirect, g, render_template, Response, make_response
from flask_caching import Cache
from urllib.parse import quote
from math import pi
import numpy as np

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# API Keys
client_id = "26b7856504274aaf8e73196314a11837"
client_secret = "090108ca091346288c6c27e0d0eec073"

# API URLs
auth_url = "https://accounts.spotify.com/authorize"
token_url = "https://accounts.spotify.com/api/token"
base_url = "https://api.spotify.com/v1"

# Redirect uri and authorization scopes
redirect_uri = "http://127.0.0.1:8080/welcome"
scope = "user-top-read user-read-recently-played playlist-read-collaborative playlist-read-private"

# Image folder configuration
CUR_DIR = os.getcwd()
IMG_DIR = os.path.join(CUR_DIR, "/templates/images/energy.jpg")
app.config['UPLOAD_FOLDER'] = "/static/"

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


# GET a user's top artists
def get_top_artist_data(auth_header, time_range, limit):
    endpoint = "{}/me/top/artists?time_range={}&limit={}".format(base_url, time_range, limit) 
    response = requests.get(endpoint, headers=auth_header)
    data = json.loads(response.text)
    top_artist_data = extract.top_artists(data)
    return top_artist_data


# GET a user's top tracks
def get_top_tracks_data(auth_header, time_range, limit):
    endpoint = "{}/me/top/tracks?time_range={}&limit={}".format(base_url, time_range, limit) 
    response = requests.get(endpoint, headers=auth_header)
    data = json.loads(response.text)
    top_tracks_data = extract.top_tracks(data)
    return top_tracks_data


# GET a user's top tracks grouped by their top artists
def get_top_tracks_by_artist(auth_header):
    top_tracks = get_top_tracks_data(auth_header, 'long_term', '50')
    top_artists = get_top_artist_data(auth_header, 'long_term', '10')
    result = extract.top_tracks_by_artist(top_tracks, top_artists)
    return result


# GET a user's recent listening history
def get_recent_tracks_data(auth_header, limit):
    endpoint = "{}/me/player/recently-played?type=track&limit={}".format(base_url, limit)
    response = requests.get(endpoint, headers=auth_header)
    data = json.loads(response.text)
    recent_tracks_data = extract.recent_tracks(data)
    return recent_tracks_data


# GET the track ids from the user's recent listening history
def get_recent_tracks_ids(auth_header, limit):
    endpoint = "{}/me/player/recently-played?type=track&limit={}".format(base_url, limit)
    response = requests.get(endpoint, headers=auth_header)
    data = json.loads(response.text)
    recent_track_ids = extract.recent_track_ids(data)
    result = ','.join(recent_track_ids)
    return result


# GET the track ids for the user's top tracks
def get_top_tracks_ids(auth_header, time_range, limit):
    endpoint = "{}/me/top/tracks?time_range={}&limit={}".format(base_url, time_range, limit) 
    response = requests.get(endpoint, headers=auth_header)
    data = json.loads(response.text)
    top_tracks_id = extract.top_track_ids(data)
    result = ','.join(top_tracks_id)
    return result


# GET the artwork of tracks
def get_track_images(auth_header, track_ids):
    endpoint = "{}/tracks?ids={}".format(base_url, track_ids)
    response = requests.get(endpoint, headers=auth_header)
    data = json.loads(response.text)
    track_images = extract.track_images(data)
    return track_images


# GET the images of artists
def get_artist_images(auth_header, artist_ids):
    endpoint = "{}/artists?ids={}".format(base_url, artist_ids)
    response = requests.get(endpoint, headers=auth_header)
    data = json.loads(response.text)
    artist_images = extract.artist_images(data)
    return artist_images


# GET the image urls of the top tracks
def get_top_track_images(auth_header, tracks):
    lst = []
    for item in tracks:
        track_id = item[1]
        lst.append(track_id)
    track_ids = ','.join(lst)
    images = get_track_images(auth_header, track_ids)
    return images


# GET the image urls of the top artists
def get_top_artist_images(auth_header, artists):
    lst = []
    for item in artists:
        artist_id = item[1]
        lst.append(artist_id)
    artist_ids = ','.join(lst)
    images = get_artist_images(auth_header, artist_ids)
    return images


# GET the tracks from a playlist
def get_tracks_from_playlist(auth_header, list_id, person_type):
    endpoint = "{}/playlists/{}/tracks".format(base_url, list_id)
    response = requests.get(endpoint, headers=auth_header)
    data = json.loads(response.text)
    datapoints = get_dataframe(auth_header, data, person_type)
    return datapoints


# Function that can be called by a route based on term length
def display_top_tracks(term_length):
    # Get the access token from its cookie and use it to access data
    access_token = request.cookies.get('token')
    auth_header = {"Authorization": "Bearer {}".format(access_token)}
    top_tracks_data = get_top_tracks_data(auth_header, term_length, '30')
    images = get_top_track_images(auth_header, top_tracks_data)
    return (top_tracks_data, images)


# Function that can be called by a route based on term length
def display_top_artists(term_length):
    # Get the access token from its cookie and use it to access data
    access_token = request.cookies.get('token')
    auth_header = {"Authorization": "Bearer {}".format(access_token)}
    top_artist_data = get_top_artist_data(auth_header, term_length, '30')
    images = get_top_artist_images(auth_header, top_artist_data)
    return (top_artist_data, images)


# Function that can be called by a route based on term length
def display_top_tracks_by_artist(term_length):
    # Get the access token from its cookie and use it to access data
    access_token = request.cookies.get('token')
    auth_header = {"Authorization": "Bearer {}".format(access_token)}
    data = get_top_tracks_by_artist(auth_header)
    lst = []
    for item in data:
        lst.append(item)
    images = get_top_artist_images(auth_header, lst)
    return (data, images)


# GET audio features for several tracks and store necessary datapoints
def do_audio_analysis(auth_header, track_ids):
    endpoint = "{}/audio-features?ids={}".format(base_url, track_ids)
    response = requests.get(endpoint, headers=auth_header)
    data = json.loads(response.text)
    datapoints = extract.get_audio_datapoints(data)
    return datapoints


# Graph data using matplotlib and seaborne
def make_graph(datapoints, tag):
    df = pd.DataFrame()
    df['Top Song Number'] = range(1, len(datapoints[tag]) + 1)
    y_title = tag.capitalize()
    df[y_title] = datapoints[tag]
    title = y_title + " ratings of your top songs!"
    sns_plot = sns.barplot(x="Top Song Number", y=y_title, data=df).set_title(title)
    fig = sns_plot.get_figure()
    fig.set_size_inches(15, 7.5)   
    fig.savefig('static/{t}.png'.format(t=tag))


# Returns a pandas dataframe containing data from the audio analysis
def get_dataframe(auth_header, data, label):
    df = pd.DataFrame()
    items = data['items'] 
    string_ids = ""
    for track in items:
        track_id = track['track']['id']
        string_ids += track_id
        string_ids += ','
    string_ids = string_ids[:-1]
    datapoints = do_audio_analysis(auth_header, string_ids)
    df['Danceability'] = datapoints['danceability']
    df['Tempo'] = datapoints['tempo']
    df['Instrumentalness'] = datapoints['instrumentalness']
    df['Energy'] = datapoints['energy']
    df['Acousticness'] = datapoints['acousticness']
    df['Valence'] = datapoints['valence']
    df['Liveness'] = datapoints['liveness']
    df['Loudness'] = datapoints['loudness']
    df['Speechiness'] = datapoints['speechiness']
    df['Label'] = [label] * (len(df.index))
    return df


# Creates a radar chart
def make_radar_chart(predictions):
    labels = np.array(["Outgoing", "Mellow", "Introverted"])
    stats = [0, 0, 0]
    for num in predictions:
        if num == 2:
            stats[0] += 1
        elif num == 1:
            stats[1] += 1
        else:
            stats[2] += 1
    stats = np.array(stats)
    angles = np.linspace(0, 2*np.pi, len(labels), endpoint=False)
    stats = np.concatenate((stats,[stats[0]]))
    angles = np.concatenate((angles,[angles[0]]))
    fig = plt.figure()
    ax = fig.add_subplot(111, polar=True,facecolor='black',frameon=True)
    ax.plot(angles, stats)
    ax.fill(angles, stats, alpha=0.25)
    ax.set_thetagrids(angles * 180/np.pi, labels)
    ax.set_title("Personality Graph")
    # ax.grid(True)
    fig.set_size_inches(15, 7.5)   
    fig.savefig("static/images/personality.png")


# Return predictions from the ML model
def model_predict(datapoints):
    df = pd.DataFrame()
    df['Danceability'] = datapoints['danceability']
    df['Tempo'] = datapoints['tempo']
    df['Instrumentalness'] = datapoints['instrumentalness']
    df['Energy'] = datapoints['energy']
    df['Acousticness'] = datapoints['acousticness']
    df['Valence'] = datapoints['valence']
    df['Liveness'] = datapoints['liveness']
    df['Loudness'] = datapoints['loudness']
    df['Speechiness'] = datapoints['speechiness']
    xgb_loaded = pickle.load(open('xgb.pkl', 'rb'))
    predictions = xgb_loaded.predict(df)
    return predictions


# Initial route for user authentication with Spotify
@app.route("/")
def index():
    # Redirects the user to the Spotify login page (first thing that happens upon app launch)
    url_args = "&".join(["{}={}".format(key, quote(val)) for key, val in auth_query.items()])
    authorization = "{}/?{}".format(auth_url, url_args)
    response = make_response(redirect(authorization))
    response.set_cookie('token', 'deletion', max_age=0)
    return response


# Homepage of application
@app.route("/welcome")
def display_top_data():
    with app.app_context():
        cache.clear()
    # Get an access token from its cookie or generate one if it doesn't exist yet
    access_token = request.cookies.get('token')
    if access_token == None:
        access_token = generate_access_token()

    # Use the token to get the necessary authorization header and access data
    auth_header = {"Authorization": "Bearer {}".format(access_token)}
    recent_tracks_data = get_recent_tracks_data(auth_header, '50')
    recent_track_ids = get_recent_tracks_ids(auth_header, '50')
    track_images = get_track_images(auth_header, recent_track_ids)

    # Store HTML rendering in a response and create a cookie for the access token
    response = make_response(render_template("index.html", recent=recent_tracks_data, images=track_images))
    response.set_cookie('token', access_token, max_age=3600)
    return response


# Page for viewing top tracks in the past 1 month
@app.route("/top-tracks-short-term")
def display_top_tracks_short_term():
    data = display_top_tracks('short_term')
    return render_template("toptracks.html", top_tracks=data[0], images=data[1], short_link_status="active", 
                            med_link_status="", long_link_status="") 


# Page for viewing top tracks in the past 6 months
@app.route("/top-tracks-medium-term")
def display_top_tracks_medium_term():
    data = display_top_tracks('medium_term')
    return render_template("toptracks.html", top_tracks=data[0], images=data[1], short_link_status="", 
                            med_link_status="active", long_link_status="") 


# Page for viewing all time top tracks
@app.route("/top-tracks-long-term")
def display_top_tracks_long_term():
    data = display_top_tracks('long_term')
    return render_template("toptracks.html", top_tracks=data[0], images=data[1], short_link_status="", 
                            med_link_status="", long_link_status="active") 


# Page for viewing top artists in the past month
@app.route("/top-artists-short-term")
def display_top_artists_short_term():
    data = display_top_artists('short_term')
    return render_template("topartists.html", top_artists=data[0], images=data[1], short_link_status="active", 
                            med_link_status="", long_link_status="") 


# Page for viewing top artists in the past 6 months
@app.route("/top-artists-medium-term")
def display_top_artists_medium_term():
    data = display_top_artists('medium_term')
    return render_template("topartists.html", top_artists=data[0], images=data[1], short_link_status="", 
                            med_link_status="active", long_link_status="") 


# Page for viewing all time top artists
@app.route("/top-artists-long-term")
def display_top_artists_long_term():
    data = display_top_artists('long_term')
    return render_template("topartists.html", top_artists=data[0], images=data[1], short_link_status="", 
                            med_link_status="", long_link_status="active") 


# Page for viewing top tracks grouped by artist
@app.route("/top-tracks-by-artist")
def display_top_tracks_by_artist_short_term():
    data = display_top_tracks_by_artist('short_term')
    return render_template("toptracksbyartist.html", content=data[0], images=data[1])


# Page for viewing an audio analysis graphS
@app.route("/audio-analysis")
@cache.cached(timeout=60)
def audio_analysis():
    # Get the access token from its cookie and use it to access data
    access_token = request.cookies.get('token')
    auth_header = {"Authorization": "Bearer {}".format(access_token)}
    track_ids = get_top_tracks_ids(auth_header, 'long_term', '50')
    
    # Create a graph using datapoints
    datapoints = do_audio_analysis(auth_header, track_ids)
    matplotlib.use('Agg')
    matplotlib.style.use('ggplot')
    sns.set_style('dark')
    for key in datapoints:
        make_graph(datapoints, key)

    # Render HTML with the desired data
    img_names = ['danceability.png','energy.png', 'instrumentalness.png','tempo.png']
    img_1_file = os.path.join(app.config['UPLOAD_FOLDER'], 'danceability.png')
    img_2_file = os.path.join(app.config['UPLOAD_FOLDER'], 'energy.png')
    img_3_file = os.path.join(app.config['UPLOAD_FOLDER'], 'instrumentalness.png')
    img_4_file = os.path.join(app.config['UPLOAD_FOLDER'], 'tempo.png')
    response = make_response(render_template("audioanalysis.html", img_1 = img_1_file, img_2 = img_2_file, img_3 = img_3_file, img_4 = img_4_file))
    return response


# Page for viewing a user's sentiment analysis
@app.route("/personality-analysis")
def predict_personality():
    access_token = request.cookies.get('token')

    auth_header = {"Authorization": "Bearer {}".format(access_token)}
    """
    3 Personality types instead of 5 
    Outgoing/extraversion/energetic Type A - 0
    Mellow/Chill/peaceful Type B = 1
    Submissive/conformist/passive  Type C = 2
    """
    frame_list = []
    # 476 songs
    outgoing_list = ['37i9dQZF1DX3rxVfibe1L0', '37i9dQZF1DX6GwdWRQMQpq','37i9dQZF1DXdVbxH0H5oTi','37i9dQZF1DXdPec7aLTmlC', '37i9dQZF1DWSf2RDTDayIx', '37i9dQZF1DX7KNKjOK0o75']
    # ~300 songs
    mellow_list = ['37i9dQZF1DX6ziVCJnEm59', '37i9dQZF1DWSiZVO2J6WeI', '37i9dQZF1DX4E3UdUs7fUx', '37i9dQZF1DWYiR2Uqcon0X', '37i9dQZF1DWUvQoIOFMFUT', '37i9dQZF1DWXe9gFZP0gtP', 
    '37i9dQZF1DWZqd5JICZI0u', '17HYiAIcwlDEg5RgVkm4L7']
    # 413 songs
    passive_list = ['37i9dQZF1DX3YSRoSdA634','37i9dQZF1DX7gIoKXt0gmx','37i9dQZF1DWX83CujKHHOn', '37i9dQZF1DWSqBruwoIXkA', '37i9dQZF1DWVrtsSlLKzro', '19Bsw8qePEz1l5kQ4jWUvw']

    for item in passive_list:
        frame_list.append(get_tracks_from_playlist(auth_header, item, 2))
    for item in mellow_list:
        frame_list.append(get_tracks_from_playlist(auth_header, item, 1))
    for item in outgoing_list:
        frame_list.append(get_tracks_from_playlist(auth_header, item, 0))
    result = pd.concat(frame_list)
    result.to_csv(r'tracks.csv', index = False)
    track_ids = get_top_tracks_ids(auth_header, 'long_term', '50')
    datapoints = do_audio_analysis(auth_header, track_ids)
    predictions = model_predict(datapoints)
    make_radar_chart(predictions)
    return render_template("person.html")


# Logs the user out of the application
@app.route("/logout")
def logout():
    return redirect("https://www.spotify.com/logout/")


# Disables image caching
@app.after_request
def disable_cache(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate public, max-age=0"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    return r


# Run the server
if __name__ == "__main__":
    app.run(debug=True, port=8080)
