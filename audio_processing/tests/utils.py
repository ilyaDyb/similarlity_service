import os
import requests
import lxml

from bs4 import BeautifulSoup

class DownloadMusicProccess:
    """
    1.0.0: for now it will work for a specific site with specific tags, later I will make it more universal mb)
    this will definitely work on the site https://rus.hitmotop.com/genre/209
    """

    BASE_PATH = "audio_processing/tests/computing/test_audios/"


    def __init__(self, page_url: str, download_folder: str) -> None | ValueError:
        download_path = f"{self.BASE_PATH}{download_folder}/"
        if not os.path.exists(download_path):
            raise ValueError("download_folder does not exists")
        self.page_url: str = page_url
        self.download_path: str = download_path


    def get_song_links(self):
        response = requests.get(self.page_url)
        with open("test.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        soup = BeautifulSoup(response.text, 'lxml')

        song_links = []
        for a_tag in soup.find_all('a', class_='track__download-btn'):
            song_url = a_tag['href']
            song_name = song_url.split('/')[-1]
            song_links.append((song_url, song_name))

        return song_links


    def download_file(self, song_links):
        if not song_links:
            raise ValueError("No song links found")
        
        max_num_in_test_audios = self.__get_max_num_from_test_files() + 1

        for song_url, _ in song_links:
            if len(str(max_num_in_test_audios)) == 1:
                song_name = f"example0{max_num_in_test_audios}.mp3"
            else:
                song_name = f"example{max_num_in_test_audios}.mp3"

            response = requests.get(song_url, stream=True)
            file_path = os.path.join(self.download_path, song_name)
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            max_num_in_test_audios += 1

            print(f'Downloaded: {song_name}')


    def __get_max_num_from_test_files(self) -> int:
        files = os.listdir(self.download_path)

        max_value = 0
        for file in files:
            value = file.split(".")[0][-2:]
            if value == "":
                continue

            if value[0] == "0":
                value = value[1]

            max_value = max(max_value, int(value))
        return max_value

# Example for use

download_proccess = DownloadMusicProccess("https://rus.hitmotop.com/artist/37933/start/48", "similar") # oprional .../209/48 - this is smth like offset
links = download_proccess.get_song_links()
download_proccess.download_file(links)
print(links)
files = os.listdir(download_proccess.download_path)
