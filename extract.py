# Returns a list of the user's top 10 artists
def top_artists(data, tag):
    artists = []
    items = data['items']
    for item in items:
        artist_name = item[tag]
        artists.append(artist_name)
    return artists


# Returns a list of the user's top 10 tracks
def top_tracks(data, tag):
    tracks = {}
    for item in data['items']:
        track_name = item[tag]
        artist_name = item['artists'][0][tag]
        tracks[track_name] = artist_name
    return tracks


# Returns a dictionary with recently listened to tracks grouped by artist
def recent_tracks(data):
    recents = {}
    num_listens = {}
    for item in data['items']:
        track_name = item['track']['name']
        artist_name = item['track']['artists'][0]['name']
        artist_id = item['track']['artists'][0]['id']
        recents[track_name] = (artist_name, artist_id)
        if artist_id in num_listens:
            num_listens[artist_id] = num_listens[artist_id] + 1
        else:
            num_listens[artist_id] = 1
    trending_id = trending_artist(num_listens)
    return [recents, trending_id]


# Returns the artist id of an artist that the user has been listening to a lot recently
def trending_artist(num_listens):
    max_plays = 0
    result = ""

	# Keep track of which artist has the highest number of recent plays
    for artist_id in num_listens:
        num_plays = num_listens.get(artist_id)
        if num_plays > max_plays:
            max_plays = num_plays
            result = artist_id
	
    # If that maxiumum is greater than 5, the aritst qualifies as a frequent listen
    if max_plays >= 5:
        return result
    else:
        return None

# Returns a list of an artist's related artists
def related_artists(data):
    result = []
    for artist in data['artists']:
        result.append(artist['name'])
        print(artist['name'])
    return result

# Returns a dictionary with the top 50 tracks grouped by artist
def top_tracks_by_artist(top_tracks, top_artists):
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