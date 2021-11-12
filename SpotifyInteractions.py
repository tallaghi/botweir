import spotipy
import math
import re
import mySQLHelper
from spotipy.oauth2 import SpotifyOAuth
from collections import Counter
import random


# A callback URL is needed here for initial OAuth, I used a local flask site to get it going
def log_in_to_spotify(SPOT_ID,SPOT_SECRET):
    access_token = ""
    scope = "user-library-read playlist-read-collaborative playlist-modify-public playlist-read-private playlist-modify-private user-read-email user-read-private"        
    sp_oauth = SpotifyOAuth(client_id=SPOT_ID,client_secret=SPOT_SECRET,redirect_uri='http://127.0.0.1:5000/spotify/callback',scope=scope)
    token_info = sp_oauth.get_cached_token()

    if token_info:
        access_token = token_info['access_token']
        sp = spotipy.Spotify(access_token)
    return sp

def create_playlist(SPOT_ID,SPOT_SECRET,channel_name):
    sp = log_in_to_spotify(SPOT_ID,SPOT_SECRET)
    playlist_name = "ThisChord_" + channel_name
    pl = sp.user_playlist_create(sp.me()['id'],playlist_name,public=True,collaborative=False)
    print(pl["id"])
    return pl["id"]

def create_playlist(sp,channel_name):
    playlist_name = "ThisChord_" + channel_name
    pl = sp.user_playlist_create(sp.me()['id'],playlist_name,public=True,collaborative=False)
    print(pl["id"])
    return pl["id"]

def get_most_popular_song_on_album(sp,albumId):
    pageSize = 50 # MAX ALLOWED
    firstAlbumTracks = sp.album_tracks(albumId)
    albumTracks = firstAlbumTracks["items"]
    total = firstAlbumTracks["total"]

    while len(albumTracks) < total:
        albumTracks.extend(sp.album_tracks(albumId,limit=pageSize,offset=len(albumTracks))["items"])

    mostPopularTrackId = ""
    mostPopularNum = 0
    for item in albumTracks:
        trackInfo = sp.track(item["id"])
        if (mostPopularNum == 0 and trackInfo["popularity"] >= mostPopularNum) or trackInfo["popularity"] > mostPopularNum :
            mostPopularTrackId=trackInfo["id"]
            mostPopularNum=trackInfo["popularity"]
    print(f"{mostPopularTrackId} {mostPopularNum}")
    return mostPopularTrackId


def parse_ids_from_message(message,sp):
    urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message)
    t_ids = []
    for url in urls:
        if "https://open.spotify.com/track/" in url:
            t_id = url.replace("https://open.spotify.com/track/","")
            if len(t_id) > 22:
                t_id = t_id[0:t_id.index("?")]
            t_ids.append(t_id)
        elif "https://open.spotify.com/album/" in url:
            a_id = url.replace("https://open.spotify.com/album/","")
            if len(a_id) > 22:
                a_id = a_id[0:a_id.index("?")]
            #t_id = sp.album_tracks(t_id,limit=1,offset=0)["items"][0]["id"]
            t_id = get_most_popular_song_on_album(sp,a_id)
            t_ids.append(t_id)
    return t_ids

def get_channel_playlist(channel_name):
    playlist_id = mySQLHelper.get_playlist_by_channel(channel_name)
    if playlist_id == "":
        return "There is no playlist for this channel. Add a track or album to create a playlist!"
    return "The playlist for this channel is https://open.spotify.com/playlist/" + playlist_id

def add_track_ids_to_playlist(sp, t_ids, channel_name):
    playlist_id = mySQLHelper.get_playlist_by_channel(channel_name) 
    if playlist_id == "":
        playlist_id = create_playlist(sp,channel_name)
        mySQLHelper.insert_channel_playlist(channel_name, playlist_id)        
    track_list = get_tracks_from_playlist(sp,playlist_id)
    for t_id in t_ids:
        if t_id not in track_list:
            sp.playlist_add_items(playlist_id,[t_id])
    
    return "https://open.spotify.com/playlist/" + playlist_id

def add_tracks_to_playlist(SPOT_ID,SPOT_SECRET,message,channel_name):    
    sp = log_in_to_spotify(SPOT_ID,SPOT_SECRET)
    
    t_ids = parse_ids_from_message(str(message),sp)
    response = add_track_ids_to_playlist(sp, t_ids, channel_name)
    add_track_ids_to_playlist(sp, t_ids, "master-playlist")
    return response

def recommend_based_on_playlist(SPOT_ID,SPOT_SECRET,channel_name):
    playlist_id = mySQLHelper.get_playlist_by_channel(channel_name)
    sp = log_in_to_spotify(SPOT_ID,SPOT_SECRET)
    response = ""

    pageSize = 100 # MAX ALLOWED
    firstPlaylistTracks = sp.playlist_tracks(playlist_id)
    total = firstPlaylistTracks["total"]
    artistSeedIds = []
    trackSeedIds = []
    
    if total != 0:
        if total > 5:
            tseedIds = [item["id"] for sublist in [pt["track"]["artists"] for pt in firstPlaylistTracks["items"]] for item in sublist]    
            if total > pageSize:
                localAmt = pageSize
                while localAmt < total:
                    tseedIds.extend([item["id"] for sublist in [pt["track"]["artists"] for pt in sp.playlist_tracks(playlist_id,limit=pageSize,offset=localAmt)["items"]] for item in sublist])
                    localAmt += pageSize
            seedCounter = Counter(tseedIds)
            artistSeedIds = [s[0] for s in seedCounter.most_common(5)]

        if total <= 5 or (total > 5 and len(artistSeedIds) < 5):
            sampleSize = (total if total < 5 else 5-len(artistSeedIds))
            trackSeedIds = random.sample([pt["track"]["id"] for pt in sp.playlist_tracks(playlist_id)["items"]],(sampleSize))
        
        reco = sp.recommendations(seed_tracks=trackSeedIds,seed_artists=artistSeedIds,limit=3)
        trackUrls = [track["external_urls"]["spotify"] for track in reco["tracks"]]
        response = f":thinking: try these out! {trackUrls[0]} {trackUrls[1]} {trackUrls[2]}"

    else:        
        response = "There are no tracks in this channel's playlist. Add some tracks to get recommendations!"

    return response

def compile_master_playlist(SPOT_ID,SPOT_SECRET):
    sp = log_in_to_spotify(SPOT_ID,SPOT_SECRET)
    response = ""
    channel_name = "master-playlist"
    tracks = []
    master_playlist_id = mySQLHelper.get_playlist_by_channel(channel_name)
    if master_playlist_id == "":
        master_playlist_id = create_playlist(sp,channel_name)
        mySQLHelper.insert_channel_playlist(channel_name, master_playlist_id)    
    
    master_tracks = get_tracks_from_playlist(sp,master_playlist_id)

    playlist_ids = mySQLHelper.get_all_playlists()
    if playlist_ids:
        for playlist_id in playlist_ids:
            tracks = tracks + get_tracks_from_playlist(sp,playlist_id)
    else:
        response = "zap fucked up"
    
    unique_tracks = list(set(tracks))

    for track in unique_tracks:
        if track not in master_tracks:
            sp.playlist_add_items(playlist_id,[track])

    response = "It worked"

    return response

def get_tracks_from_playlist(sp, playlist_id):
    tracks_first_call = sp.playlist_tracks(playlist_id, fields='total,limit,next,items(track(id))')
    track_list = []
    for item in tracks_first_call["items"]:
        track_list.append(item["track"]["id"])

    if tracks_first_call["total"] > tracks_first_call["limit"]:
        tracks_left = tracks_first_call["total"] - tracks_first_call["limit"]        
        calls_left = math.ceil(tracks_left / tracks_first_call["limit"])            
        for x in range(calls_left):
            offset = ((x+1)*100)
            tracks = sp.playlist_tracks(playlist_id, fields='total,limit,next,items(track(id))',offset=offset)
            for item in tracks["items"]:
                track_list.append(item["track"]["id"])

    return track_list