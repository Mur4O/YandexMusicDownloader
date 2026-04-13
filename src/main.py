import os
import re
import time
import eyed3
import logging
from pathlib import Path
from yandex_music import Client

logging.getLogger('eyed3.mp3.headers').setLevel(logging.ERROR)

# Выставляем рабочую директорию
base_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(base_path)

# Создаём папку если не существует
folder_path = "./Музыка"
os.makedirs(folder_path, exist_ok=True)

# Создаём кэш если не существует
file_path = Path("downloading.txt")
file_path.touch(exist_ok=True)

# Определяем пользователя
with open('token.txt', 'r', encoding='utf-8') as f:
    token = f.read().strip()
client = Client(token=token).init()

# Вытягиваем любимые треки
liked_tracks = client.users_likes_tracks()
i = 0
with open('downloading.txt', 'r+', encoding='utf-8') as f:
    data = f.readlines()
    for id in data:
        data[data.index(id)] = id.replace('\n', '') # Поиск в файлике-кэше
    
    for track in liked_tracks:
        i += 1
        if not track.id in data:
            f.seek(0, 2)  # Перемещаемся в конец файла
            f.write(f'{track.id}\n')
            
            track = track.fetch_track()
            album = client.albums_with_tracks(track.albums[0].id)
            raw_name = f'{track.artists[0].name} - {album.title}'
            clean_name = re.sub(r'[<>:"/\\|?*]', '', raw_name) # Экранирование от кривых названий
            album_path = f'./Музыка/{clean_name}'
            os.makedirs(album_path, exist_ok=True)
            
            cover_bytes = album.download_cover_bytes(size='1000x1000')
            
            # Перебираем все диски и треки в альбоме
            for volume in album.volumes:
                for track in volume:
                    raw_name = f'{track.artists[0].name} - {track.title}'
                    clean_name = re.sub(r'[<>:"/\\|?*]', '', raw_name) # Экранирование от кривых названий
                    file_path = f'{album_path}/{clean_name}.mp3'
                    track.download(file_path)
                    
                    time.sleep(0.1)
            
                    audiofile = eyed3.load(file_path)
                    if audiofile.tag is None:
                        audiofile.initTag()
                        
                    audiofile.tag.images.set(3, cover_bytes, "image/jpeg")
                    audiofile.tag.artist = track.artists[0].name
                    audiofile.tag.album = album.title
                    audiofile.tag.title = track.title
                    audiofile.tag.save()
                    
                    # Перерыв перед следующим запросом
                    time.sleep(1)