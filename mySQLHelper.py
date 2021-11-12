import mysql.connector
from mysql.connector.cursor import MySQLCursorBuffered
import os
from dotenv import load_dotenv


def login_to_db():  
  load_dotenv()
  password = os.getenv('DB_PASSWORD')
  user = os.getenv('DB_USER')
  name = os.getenv('DB_NAME')
  mydb = mysql.connector.connect(
    host="localhost",
    user=user,
    password=password,
    database=name
  )
  return mydb

def get_playlist_by_channel(channel_name):
  mydb=login_to_db()
  mycursor = mydb.cursor()

  sql = "SELECT playlist_id FROM channel_playlists WHERE channel_name = %s"
  channel = (channel_name, ) 
  
  mycursor.execute(sql,channel)

  myresult = mycursor.fetchone()

  if myresult:
    playlist_id = myresult[0]
  else:
    playlist_id = ""

  mycursor.close()
  mydb.close()

  return playlist_id

def insert_channel_playlist(channel_name,playlist_id):
  mydb=login_to_db()
  mycursor = mydb.cursor()

  add_playlist = ("INSERT INTO channel_playlists "
               "(channel_name, playlist_id) "
               "VALUES (%s, %s)")
  data_playlist = (channel_name,playlist_id,)

  mycursor.execute(add_playlist,data_playlist)
  mydb.commit()

  mycursor.close()
  mydb.close()

def get_all_playlists():
  mydb=login_to_db()
  mycursor = mydb.cursor()

  sql = "SELECT playlist_id FROM channel_playlists"  
  
  mycursor.execute(sql)

  myresult = mycursor.fetchall()  

  if myresult:
    playlist_ids = out = [item for t in myresult for item in t]
  else:
    playlist_ids = ""
    
  mycursor.close()
  mydb.close()

  return playlist_ids


# SCHEMA
# CREATE TABLE `channel_playlists` (
#   `idchannel_playlists` int NOT NULL AUTO_INCREMENT,
#   `channel_name` varchar(145) NOT NULL,
#   `playlist_id` varchar(1000) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
#   PRIMARY KEY (`idchannel_playlists`)
# ) ENGINE=InnoDB AUTO_INCREMENT=59 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
