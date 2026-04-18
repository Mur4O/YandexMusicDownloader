import os
import re
import time
import eyed3
import logging
from pathlib import Path
from yandex_music import Client
from yandex_music import exceptions as yme

# ============================================================================================
# Сценарии работы программы:
# 1 - скачать только любимые треки в одну папку
# 2 - скачать альбомы содержащие любимые треки

scenario = 2

# ============================================================================================

logging.getLogger('eyed3').setLevel(logging.ERROR)

# Выставляем рабочую директорию
base_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(base_path)

# Создаём папку если не существует
folder_path = Path('./Музыка')
os.makedirs(folder_path, exist_ok=True)
    
# Проходимся по всем файлам .mp3 рекурсивно
downloaded = []
for mp3_file in folder_path.rglob("*.mp3"):
    audiofile = eyed3.load(str(mp3_file))
    
    try:
        user_frame = audiofile.tag.user_text_frames.get('id').text
        if user_frame:
            downloaded.append(user_frame)
    except: # Если в прошлый раз случилась ошибка в процессе скачивания файла, то удаляем его
        os.remove(mp3_file)
        print(f'Удалён файл {mp3_file}')

# Определяем пользователя
with open('token.txt', 'r', encoding='utf-8') as f:
    token = f.read().strip()
client = Client(token=token).init()

# Вытягиваем любимые треки
liked_tracks = client.users_likes_tracks()

def download():
    try:            
        for fav_track in liked_tracks:

                fav_track = fav_track.fetch_track()
                album = client.albums_with_tracks(fav_track.albums[0].id) # Обложкой песен будет обложка альбома
                print(f'Скачиваем альбом {album.title}')
                
                if scenario == 1:
                    if fav_track.id not in downloaded:
                        downloaded.append(fav_track.id)
                        download_path = f'{folder_path}/Любимые песни'
                        os.makedirs(download_path, exist_ok=True)
                        raw_name = f'{fav_track.artists[0].name} - {fav_track.title}'
                        clean_name = re.sub(r'[<>:"/\\|?*]', '', raw_name) # Экранирование от кривых названий
                        file_path = f'{download_path}/{clean_name}.mp3'
                        f.seek(0, 2)  # Перемещаемся в конец файла
                        f.write(f'{clean_name}\n')
                        fav_track.download(file_path)
                        i += 1
                        print(f'Скачан файл {fav_track.title}')
                        
                        time.sleep(0.1)
                
                        audiofile = eyed3.load(file_path)
                        if audiofile.tag is None:
                            audiofile.initTag()
                            
                        cover_bytes = album.download_cover_bytes(size='1000x1000')
                        audiofile.tag.images.set(3, cover_bytes, "image/jpeg")
                        audiofile.tag.artist = fav_track.artists[0].name
                        audiofile.tag.album = album.title
                        audiofile.tag.title = fav_track.title
                        audiofile.tag.genre = album.genre
                        audiofile.tag.save()
                        
                        # Перерыв перед следующим запросом
                        time.sleep(2)
                
                if scenario == 2:
                    raw_name = f'{album.title}'
                    clean_name = re.sub(r'[<>:"/\\|?*]', '', raw_name) # Экранирование от кривых названий
                    album_path = f'{folder_path}/{clean_name}'
                    os.makedirs(album_path, exist_ok=True)
                    
                    # Перебираем все диски и треки в альбоме
                    for volume in album.volumes:
                        for track in volume:
                            if track.id not in downloaded:
                                raw_name = f'{track.artists[0].name} - {track.title}{' ' + track.version if track.version is not None else ''}'
                                clean_name = re.sub(r'[<>:"/\\|?*]', '', raw_name) # Экранирование от кривых названий
                                file_path = f'{album_path}/{clean_name}.mp3'
                                downloaded.append(track.id)
                                track.download(file_path)
                                print(f'Скачан трек {track.title} ({track.id}) по пути {file_path}')
                                
                                time.sleep(0.1)
                        
                                audiofile = eyed3.load(file_path)
                                if audiofile.tag is None:
                                    audiofile.initTag()
                                    
                                # print(album)
                                try:
                                    try:
                                        cover_bytes = album.download_cover_bytes(size='1000x1000')
                                    except:
                                        cover_bytes = track.download_cover_bytes(size='1000x1000')
                                    audiofile.tag.images.set(3, cover_bytes, "image/jpeg")
                                except:
                                    pass
                                    
                                audiofile.tag.artist = track.artists[0].name
                                audiofile.tag.album = album.title
                                audiofile.tag.title = track.title
                                audiofile.tag.user_text_frames.set(f'{track.id}', 'id')
                                audiofile.tag.genre = album.genre
                                audiofile.tag.save()
                                
                                # Перерыв перед следующим запросом
                                time.sleep(2)
    # Перезапускаемся в случае тайм-аута
    except yme.TimedOutError as e:
        print(e)
        download()
    except yme.NetworkError as e:
        print(e)
        time.sleep(20)
        download()
        
    print('Всё скачано')
    
download()