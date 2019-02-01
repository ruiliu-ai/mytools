import zipfile
import os
import requests
import argparse

from tqdm import tqdm

parser = argparse.ArgumentParser(description='Download From Google Drive helper')
parser.add_argument('--path', type=str, default='./')

def download_file_from_google_drive(id, destination):
    URL = "https://docs.google.com/uc?export=download"
    session = requests.Session()

    response = session.get(URL, params={'id': id}, stream=True)
    token = get_confirm_token(response)

    if token:
        params = {'id': id, 'confirm': token}
        response = session.get(URL, params=params, stream=True)

    save_response_content(response, destination)


def get_confirm_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value
    return None


def save_response_content(response, destination, chunk_size=32 * 1024):
    total_size = int(response.headers.get('content-length', 0))
    with open(destination, "wb") as f:
        for chunk in tqdm(
                response.iter_content(chunk_size),
                total=total_size,
                unit='B',
                unit_scale=True,
                desc=destination):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)


if __name__ == '__main__':
    args = parser.parse_args()
    dirpath = args.path
    os.makedirs(dirpath, exist_ok=True)

    filenames = [
        'deltas00000.zip', 'deltas01000.zip'
    ]

    drive_ids = [
        '0B4qLcYyJmiz0TXdaTExNcW03ejA', '0B4qLcYyJmiz0TjAwOTRBVmRKRzQ'
    ]

    for filename, drive_id in zip(filenames, drive_ids):
        print('Deal with file: ' + filename)
        save_path = os.path.join(dirpath, filename)

        if os.path.exists(save_path):
            print('[*] {} already exists'.format(save_path))
        else:
            download_file_from_google_drive(drive_id, save_path)
