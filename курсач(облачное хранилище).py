from pprint import pprint
from tqdm import tqdm
import requests
import json

# получаем json файл с нашими фотографиями
def my_foto(user_id,access_token,version='5.199'):
    vk_url = 'https://api.vk.com/method/photos.get'
    params = {
        'owner_id': user_id,
        'album_id': 'wall',
        'extended': 1,
        'photo_sizes': 1,
        'access_token': access_token, 
        'v': version
        }
    response = requests.get(vk_url, params=params).json()
    return (response['response']['items'])

# фильтруем рамеры и оставляем только максимальные размеры
def process_photos(photos, count=5):
    processed = []
    for photo in photos:
        likes = photo['likes']['count']
        date = photo['date']
        max_size = max(photo['sizes'], key=lambda s: s['width'] * s['height'])
        processed.append({
            'likes': likes,
            'date': date,
            'url': max_size['url'],
            'size_type': max_size['type']
        })
    processed.sort(key=lambda x: x['url'].split('size=')[-1], reverse=True)
    return processed[:count]
    
# создаем повую папку на яндекс диске
def creating_folder(folder_name,yandex_token):
    yd_url_folder = 'https://cloud-api.yandex.net/v1/disk/resources'
    params = {
        'path':f'{folder_name}'  #название нашей новой папки
        }
    headers = {
        'Authorization': f'{yandex_token}'
        }
    response = requests.put(yd_url_folder, params=params, headers=headers)
        
# добавление фото на яндекс диск 
def upload_to_yandex(yandex_token, folder, selected_photos):
    uploaded = []
    for photo in tqdm(selected_photos,colour= 'green', desc='Загрузка фотографий'):
        file_name = f"{photo['likes']}.jpg"
        if any(f['file_name'] == file_name for f in uploaded):
            file_name = f"{photo['likes']}_{photo['date']}.jpg"
       
        yd_url_get_uplink = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        headers = {
            'Authorization': f'{yandex_token}'
            }
        params = {
            'path': f'{folder}/{file_name}',
            'url': photo['url']
            }
        response = requests.post(yd_url_get_uplink, params=params, headers=headers)
        if response.status_code == 202:
            uploaded.append({
                'file_name':f'{file_name}',
                'size': photo['size_type']
                            })
    return uploaded

def main():
                               
    user_id = input('Введите id пользователя: ')
    access_token = input('Введите token пользователя: ')
    folder_name = input('Как бы вы хотели назвать папку: ')
    yandex_token = input('Введите yandex_token: ')

    photos = my_foto(user_id, access_token)
    selected_photos = process_photos(photos)
    creating_folder(folder_name, yandex_token)
    uploaded_info = upload_to_yandex(yandex_token, folder_name, selected_photos)
    
    with open('photos_info.json', 'w') as f:
        json.dump(uploaded_info, f, indent=4)
    
    print("\nВыполненно! Проверте Yandex Disk и файл photos_info.json") 
     
if __name__ == '__main__':
    main()