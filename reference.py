# Returns a python dictionary with the top 50 tracks grouped by the artist
def top_tracks_by_artist(range):
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

# Returns a user's 30 most recently listened tracks
# Also returns each artist's play frequency in those top 30
def get_user_recent_data():
	tracks = {}
	num_listens = {}

	# Continue if token is valid
	if token:
		# Get the metadata for the recently played tracks
		sp = spotipy.Spotify(auth=token)
		results = sp.current_user_recently_played(limit=30, after=None, before=None)
		
		# Parse metadata to obtain what we need
		for item in results['items']:
			# Get a track and its corresponding artist and store them
			track_id = item['track']['id']
			artist_id = item['track']['artists'][0]['id']
			tracks[track_id] = artist_id
			# Update the entry if it exists, otherwise make a new one
			if artist_id in num_listens:
				num_listens[artist_id] = num_listens[artist_id] + 1
			else:
				num_listens[artist_id] = 1
	else:
		print("Can't get token")
	return [tracks, num_listens]


# Gets a users top 10 artists and top 10 tracks
def get_user_top_data(range):
	top_artists = []
	top_tracks = {}

	# Continue if token is valid
	if token:
		# Get the metadata for the top artists and tracks
		sp = spotipy.Spotify(auth=token)
		artist_data = sp.current_user_top_artists(limit=10, offset=0, time_range=range)
		track_data = sp.current_user_top_tracks(limit=10, offset=0, time_range=range)

		# Parse the metadata and store the IDs of the top 10 artists
		for item in artist_data['items']:
			artist_id = item['id']
			top_artists.append(artist_id)

		# Parse the metadata again and store the top 10 tracks and each one's corresponding artist
		for item in track_data['items']:
			# Get a track and the corresponding artist and store it
			track_id = item['id']
			artist_id = item['artists'][0]['name']
			top_tracks[track_id] = artist_id
	else:
		print("Can't get token")
	return [top_artists, top_tracks]


# Check to see if a user has been listening to a particular artist a lot recently
def check_for_frequent_plays(data):
	max_plays = 0
	max_artist_id = ""

	# Keep track of which artist has the highest number of recent plays
	for artist_id in data:
		num_plays = data.get(artist_id)
		if num_plays > max_plays:
			max_plays = num_plays
			max_artist_id = artist_id
	
	# If that maxiumum is greater than 5, the aritst qualifies as a frequent listen
	if max_plays >= 5:
		artist_name = sp.artist(max_artist_id)['name']
		print("You have been listening to " + artist_name + " a lot lately!")
		print("Here is a list of artists similar to " + artist_name + " that you might like:")

		# Get the artist's related artists and print them
		related_artists = get_related_artists(max_artist_id)
		for item in related_artists:
			print(sp.artist(item)['name'])

	# Print a default message if there is no recent artist frequently listened to
	else:
		print("You have been listening to a variety of different artists lately!")


# Returns a list of an artist's related artists
def get_related_artists(artist_id):
	data = sp.artist_related_artists(artist_id)['artists']
	related_artists = []
	for item in data:
		related_artists.append(item['id'])
	return related_artists
