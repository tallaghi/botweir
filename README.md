This is a bot I built out over a day or two for a music based discord server I am in. It will create and associate a playlist with each text channel that is in the discord when a spotify track or album is posted in that channel. If a track is posted it gets added, if an album is posted it will find the most popular track from that album ( based on spotify plays ) and add the most popular track.

There are a handful of commands that are prefix'd by $:

$init-channel-playlist: This will historally run through the text channels in your server, create a playlist, then make all of the necessary adds required based on past messages.
$compile-master-playlist: This will initialize a master playlist that will house every track that gets added to any channel. 
$playlist: This command will post the channel specific playlist to the channel this command is run in.
$recommendations: Running this command will recommend up to 3 tracks based on the channels spotify playlist.


SETUP:

1. First you will need to generate API keys for your spotify account https://developer.spotify.com/documentation/web-api/quick-start/
    a. You will need to have a callback url to OAuth with these. 
2. Next you will need a MYSQL database somewhere, mine is hosted locally
    a. The schema for the DB is in the mySQLHelper.py. It is only 1 table.
3. Lastly you will need to set up your env file, mine looks like this:
    # .env
    DISCORD_TOKEN=
    DISCORD_GUILD=
    SPOT_CLIENT_ID=
    SPOT_CLIENT_SECRET=
    SPOT_CALLBACK=
    DB_PASSWORD=
    DB_USER=
    DB_NAME=
4. You should be set to run Main.py now, it will initially prompt you to login.