# Spotify Data App

A Flask web app that allows sptotify users to view detailed information and statistics about their usage data. Also features an audio analysis and personality classification based on the user's top songs, deployed with Microsoft Azure.

Utilizes the Spotify Web API for authentication and data collection, and uses sklearn's Decision Tree Classifier for the personality classficiation.

<h2>Links<h2>
  
 - https://developer.spotify.com/documentation/web-api/
  
 - https://scikit-learn.org/stable/modules/tree.html


## Run Commands
   ## How to run locally
   
   - You must make a few changes to the code before attempting to run it locally, the following changes are at the beginning of app.py.
   
   
   - Modify the client id and client secret variables at the beginning of app.py to reflect your own client id and secret key which you can get from the spotify developer webiste, shown below.
   
    '''
    # API Keys
    client_id = "INSERT_CLIENT_ID_HERE"
    client_secret = "INSERT_CLIENT_SECRET_KEY_HERE"
    '''
    
    '''
    # Redirect uri and authorization scopes
    redirect_uri = "https://myspotifydata.azurewebsites.net/home"
    scope = "user-top-read user-read-recently-played playlist-read-collaborative playlist-read-private"

    # UNCOMMENT TO USE FOR LOCAL TESTING
    # redirect_uri = "http://127.0.0.1:8000/home"
    '''
    
   - Uncomment the local redirect url and comment out the azurewebsites redirect urls, it should look like this when finished.
    
    '''
    # Redirect uri and authorization scopes
    #redirect_uri = "https://myspotifydata.azurewebsites.net/home"
    scope = "user-top-read user-read-recently-played playlist-read-collaborative playlist-read-private"

    # UNCOMMENT TO USE FOR LOCAL TESTING
    redirect_uri = "http://127.0.0.1:8000/home"
    '''
    
    
    
   - Additionally, you must uncomment the following block of code at the end of app.py.
    
    '''
    # # Run the server (uncomment for local testing)
    # if __name__ == "__main__":
    #    app.run(debug=True, port=8000)
    '''
    
    
    
   - Run "pip install -r requirements.txt" to install all the required dependancies, or  "pipenv install -r requirements.txt" if you are using a pipenv. 
   
   -  If all of the dependancies have been installed, run python app.py to run the Flask app locally.

      
