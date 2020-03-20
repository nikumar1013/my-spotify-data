
# Returns a list of the user's top 10 artists
def get_top_artists(data, tag):
    artists = []
    items = data['items']
    for item in items:
        artist_name = item[tag]
        artists.append(artist_name)
    return artists

# Returns a list of the user's top 10 tracks
def get_top_tracks(data, tag):
    tracks = {}
    for item in data['items']:
        track_name = item[tag]
        artist_name = item['artists'][0][tag]
        tracks[track_name] = artist_name
    return tracks


def get_recent_tracks(data,tag):
	recents = {}
	for item in data['items']:
		track_name = item['track'][tag]
		artist_name = item['track']['artists'][0][tag]
		recents[track_name] = artist_name
	return recents

# Returns a python dictionary with the top 50 tracks grouped by the artist
def get_top_tracks_by_artist(top_tracks, top_artists):
    top_tracks_by_artist = {}
    for artist in top_artists:
        tracks = []
        for track in top_tracks:
            track_artist = top_tracks.get(track)
            if artist == track_artist:
                tracks.append(track)
        if len(tracks) > 0:
        	top_tracks_by_artist[artist] = tracks
    return top_tracks_by_artist