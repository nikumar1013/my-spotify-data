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
	for item in data['items']:
		track_name = item['track']['name']
		artist_name = item['track']['artists'][0]['name']
		recents[track_name] = artist_name
	return recents


# Check to see if a user has been listening to a particular artist a lot recently
def trending_artist(recents):
    max_plays = 0
    result = ""

	# Keep track of which artist has the highest number of recent plays
    for current_artist in recents:
        num_plays = recents.get(current_artist)
        if num_plays > max_plays:
            max_plays = num_plays
            result = current_artist
	
    # If that maxiumum is greater than 5, the aritst qualifies as a frequent listen
    if max_plays >= 5:
        return result
    else:
        return None


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