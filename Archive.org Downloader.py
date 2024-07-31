import os
import requests
from bs4 import BeautifulSoup
import time

def get_file_links(url):
    print(f"Attempting to access URL: {url}")
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to access {url}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].endswith(('zip', 'rar', '7z', 'tar.gz', 'pdf', 'jpg', 'png', 'iso', 'chd'))]
    full_links = [url + link for link in links]
    print(f"Links found: {full_links}")
    return full_links

def get_remote_file_size(url):
    response = requests.head(url)
    if response.status_code == 200:
        return int(response.headers.get('content-length', 0))
    
    # Fallback if HEAD request fails
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        return int(response.headers.get('content-length', 0))
    
    print(f"Failed to access {url} to check file size.")
    return None

def download_file(url, dest_folder):
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)

    file_name = os.path.join(dest_folder, url.split('/')[-1])

    remote_file_size = get_remote_file_size(url)
    if remote_file_size is None:
        return

    local_file_size = os.path.getsize(file_name) if os.path.exists(file_name) else 0

    if os.path.exists(file_name) and local_file_size == remote_file_size:
        print(f"File already exists and has the correct size: {file_name}, skipping download.")
        return

    if os.path.exists(file_name) and local_file_size != remote_file_size:
        print(f"Incomplete file found: {file_name}, it will be replaced.")

    print(f"Starting download of: {url}")
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        downloaded_size = 0
        start_time = time.time()

        with open(file_name, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    elapsed_time = time.time() - start_time
                    speed = downloaded_size / elapsed_time if elapsed_time > 0 else 0
                    print(f"\rDownloaded: {downloaded_size} of {remote_file_size} bytes ({downloaded_size * 100 / remote_file_size:.2f}%), Speed: {speed / 1024:.2f} KB/s", end='')

        print(f"\nFile downloaded: {file_name}")
    else:
        print(f"Failed to download file: {url}")

# Ask for the URL of the directory from where you want to download the files
directory_url = input("Enter the URL of the directory: ")

# Ask for the destination directory where you want to save the files
destination_folder = input("Enter the destination folder: ")

# Get the list of file links
file_links = get_file_links(directory_url)

# Download each file
for file_link in file_links:
    download_file(file_link, destination_folder)
