
# Parses data to get a user's top 10 artists
def get_top_artists(data):
    artists = []
    items = data['items']
    for item in items:
        artist_name = item['name']
        artists.append(artist_name)
    return artists

# Parses data to get a user's top 10 tracks
def get_top_tracks(data):
    tracks = []
    for item in data['items']:
        track_name = item['name']
        artist_name = item['artists'][0]['name']
        list_entry = track_name + " - " + artist_name
        tracks.append(list_entry)
    return tracks