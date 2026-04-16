import os
import re
from pathlib import Path
from yandex_music import Client

# Авторизация
client = Client('ВАШ_ТОКЕН').init()

def download_album(album_id):
    # Получаем альбом со списком всех треков
    album = client.albums_with_tracks(album_id)
    
    # Создаем папку для альбома (очищаем название от запрещенных символов)
    album_title = re.sub(r'[<>:"/\\|?*]', '', album.title)
    album_path = Path(f"./Music/{album.artists[0].name} - {album_title}")
    album_path.mkdir(parents=True, exist_ok=True)

    print(f"Скачивание альбома: {album.title}")

    # Перебираем все диски и треки в альбоме
    for volume in album.volumes:
        for track in volume:
            # Очищаем название трека для файловой системы
            clean_track_title = re.sub(r'[<>:"/\\|?*]', '', track.title)
            file_path = album_path / f"{clean_track_title}.mp3"

            if not file_path.is_file():
                print(f"Скачиваю: {track.title}")
                track.download(str(file_path))
            else:
                print(f"Пропущено (уже есть): {track.title}")

# Пример вызова (ID альбома можно взять из ссылки в браузере)
download_album(1234567)
