
# Returns a list of the user's top 10 artists
def get_top_artists(data):
    artists = []
    items = data['items']
    for item in items:
        artist_name = item['name']
        artists.append(artist_name)
    return artists

# Returns a list of the user's top 10 tracks
def get_top_tracks(data):
    tracks = []
    for item in data['items']:
        track_name = item['name']
        artist_name = item['artists'][0]['name']
        list_entry = track_name + " - " + artist_name
        tracks.append(list_entry)
    return tracks

# Returns a python dictionary with the top 50 tracks grouped by the artist
def get_top_tracks_by_artist(range):
	dic = {}
	if token:
		sp = spotipy.Spotify(auth=token)
		track_data = sp.current_user_top_tracks(limit=50, offset=0, time_range=range)
		artist_data = sp.current_user_top_artists(limit=10, offset=0, time_range=range)
		for item in artist_data['items']:
			top_artist = item['name']
			lst = []
			for item in track_data['items']:
				track_artist = item['artists'][0]['name']
				if top_artist == track_artist:
					lst.append(item['name'])
			dic[top_artist] = lst
	return dic