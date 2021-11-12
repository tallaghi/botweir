import os
import discord
import spotipy
import json
import math
import re
import SpotifyInteractions
#from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
SPOT_ID = os.getenv('SPOT_CLIENT_ID')
SPOT_SECRET = os.getenv('SPOT_CLIENT_SECRET')

client = discord.Client()

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if "https://open.spotify.com/track/" in message.content:                
        playlist_url = ""
        response = "Track(s) added to "
        try:
            playlist_url = SpotifyInteractions.add_tracks_to_playlist(SPOT_ID,SPOT_SECRET,message.content,str(message.channel))
        except:
            response = "error!"

        response = response + "<" + playlist_url + ">"
        await message.channel.send(response)
    elif "https://open.spotify.com/album/" in message.content:  
        playlist_url = ""
        response = "Most popular track of album added to "
        try:
            playlist_url = SpotifyInteractions.add_tracks_to_playlist(SPOT_ID,SPOT_SECRET,message.content,str(message.channel))
        except:
            response = "error!"

        response = response + "<" + playlist_url + ">"
        await message.channel.send(response)

    elif "$init-channel-playlist" in message.content:
        for channel in message.guild.text_channels:
            messages = await channel.history(limit=None).flatten()#.find(lambda m: "https://open.spotify.com/track/" in m.content)
            tracks = []
            for m in messages:
                if "https://open.spotify.com/track/" in m.content: 
                    tracks.append(m.content)
                    print(m.content)

            playlist_url = ""
            error = 0
            success = 0

            for track_message in tracks:                
                try:
                    playlist_url = SpotifyInteractions.add_tracks_to_playlist(SPOT_ID,SPOT_SECRET,track_message,str(channel))
                    success += 1
                except:
                    error += 1
            
            response = str(success) + " track(s) added to " + playlist_url + "; " + str(error) + " track(s) errored;"

            await channel.send(response)
        
        await message.channel.send("done!")

    elif "$playlist" in message.content:
        response = SpotifyInteractions.get_channel_playlist(str(message.channel))
        await message.channel.send(response)

    elif "$recommendations" in message.content:
        response = SpotifyInteractions.recommend_based_on_playlist(SPOT_ID,SPOT_SECRET,str(message.channel))
        await message.channel.send(response)

    elif "$compile-master-playlist" in message.content:
        response = SpotifyInteractions.compile_master_playlist(SPOT_ID,SPOT_SECRET)
        await message.channel.send(response)

client.run(TOKEN)

