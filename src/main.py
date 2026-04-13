import os
import re
import time
import eyed3
import logging
from yandex_music import Client

logging.getLogger('eyed3.mp3.headers').setLevel(logging.ERROR)

# Выставляем рабочую директорию
base_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(base_path)

# Создаём папку если не существует
folder_path = "./Музыка"
os.makedirs(folder_path, exist_ok=True)

with open('token.txt', 'r', encoding='utf-8') as f:
    token = f.read().strip()
    
client = Client(token=token).init()

liked_tracks = client.users_likes_tracks()
i = 0
with open('downloading.txt', 'a+', encoding='utf-8') as f:
    data = f.readlines()
    
    for id in data:
        data[data.index(id)] = id.replace('\n', '')
    
    for track in liked_tracks:
        i += 1
        if not track.id in data:
            f.seek(0, 2)  # Перемещаемся в конец файла
            f.write(f'{track.id}\n')
            
            track = track.fetch_track()
            raw_name = f"{track.artists[0].name} - {track.title}"
            clean_name = re.sub(r'[<>:"/\\|?*]', '', raw_name)
            path = f'./Музыка/{clean_name}.mp3'
        
            track.download(path)
            
            time.sleep(0.1)
            
            audiofile = eyed3.load(path)
            if audiofile.tag is None:
                audiofile.initTag()
            audiofile.tag.artist = track.artists[0].name
            audiofile.tag.album = track.albums[0].title
            audiofile.tag.title = track.title
            audiofile.tag.save()
            
            # Перерыв перед следующим запросом
            time.sleep(2)
        print(f'Скачан трек номер {i}')

# print(liked_tracks[0].fetch_track().title) # Название
# print(liked_tracks[0].fetch_track().artists[0].name) # Имя артиста
# print(liked_tracks[0].fetch_track().albums[0].genre) # Жанр
# print(client.genres())
# print(liked_tracks[0].fetch_track().