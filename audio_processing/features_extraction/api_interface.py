

import os
import sys
from time import sleep
from typing import List

from dotenv import load_dotenv
import requests

load_dotenv()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

class BaseSpotifyApiInterface:
    requests_count = 0
    
    def __init__(self) -> None:
        self.client_id = os.environ.get("CLIENT_ID", None)
        self.client_secret = os.environ.get("CLIENT_SECRET", None)
        if self.client_id is None or self.client_secret is None:
            raise ValueError("Should be set client id and client secret to env")
        self.authorization = None
        self.proxies: dict[str:str] = None

    def _set_token(self) -> None:
        url = "https://accounts.spotify.com/api/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        body = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        response = requests.post(url=url, headers=headers, data=body)
        if response.status_code != 200:
            raise PermissionError("something went wrong")
        response_json = response.json()
        
        self.authorization =  f"{response_json['token_type']} {response_json['access_token']}"

    def _set_proxy(self):
        proxy_host = os.environ.get("PROXY_HOST")
        proxy_port = os.environ.get("PROXY_PORT")
        proxy_user = os.environ.get("PROXY_USER")
        proxy_password = os.environ.get("PROXY_PASSWORD")
        proxy = f"http://{proxy_user}:{proxy_password}@{proxy_host}:{proxy_port}"
        self.proxies: dict[str, str] = {
            "http": proxy,
            "https": proxy
        }

    def _get_headers(self) -> dict[str, str | None]:
        return {"Authorization": self.authorization}

    def _prepare_request(self):
        if self.authorization is None:
            self._set_token()
        if self.proxies is None:
            self._set_proxy()

    def _make_request(self, url: str, headers: dict, method="get"):
        response = requests.request(method, url, headers=headers, proxies=self.proxies)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            if not self.requests_count == 2:
                self.requests_count += 1
                self._set_token()
                sleep(2)
                return self._make_request(url, headers, method)
            else:
                raise PermissionError(f"Spotify service not working: {response.status_code}")
        elif response.status_code == 403:
            raise PermissionError("Bad proxies")
        else:
            raise ConnectionError(f"Unknown error: {response.status_code}")
        

class SpotifyApiInterface(BaseSpotifyApiInterface):

    def get_all_albums_by_atrist_id(self, artist_id: str):
        self._prepare_request()
        url = f"https://api.spotify.com/v1/artists/{artist_id}/albums"
        headers = self._get_headers()
        return self._make_request(url=url, headers=headers)
        
    def get_links_from_albums_list(self, json_data):
        return [album.get("href") for album in json_data["items"]]

    def get_data_for_tracks(self, albums_list: List[str]):
        self._prepare_request()
        headers = self._get_headers()
    
        headers = {"Authorization": self.authorization}

        tracks_credentials = []
        for album in albums_list:
            album_id = album.rsplit("/", maxsplit=1)[1]
            url = f"https://api.spotify.com/v1/albums/{album_id}/tracks"
            track_json = self._make_request(url, headers)
            
            for track in track_json.get("items"):
                tracks_credentials.append(track.get("href"))

        return tracks_credentials
        
    def get_preview_tracks_by_hrefs(self, tracks_href):
        self._prepare_request()
        tracks_credentials = []
        for href in tracks_href:
            response_json = self._make_request(
                url=href,
                headers=self._get_headers(),
                method="get"
            )
            tracks_credentials.append({
                "artists": [artist["name"] for artist in response_json.get("artists")],
                "name": response_json.get("name"),
                "preview_url": response_json.get("preview_url"),
            })
        return tracks_credentials
    
    def get_preview_tracks_from_album(self, album_id):
        self._prepare_request()
        url = f"https://api.spotify.com/v1/albums/{album_id}/tracks"
        return self._make_request(url=url, headers=self._get_headers())
    
    def get_clean_data_from_preview_json(self, json_data):
        tracks_credentials = []
        for track in json_data:
            tracks_credentials.append({
                "artists": [artist["name"] for artist in track.get("artists")],
                "name": track.get("name"),
                "preview_url": track.get("preview_url"),
            })
        return tracks_credentials

# interface = SpotifyApiInterface()
# albums_list = interface.get_all_albums_by_atrist_id("1F8usyx5PbYGWxf0bwdXwA")
# print(albums_list)
# links_albums = ['https://api.spotify.com/v1/albums/6vGmW99Q8Y3NRgQtdPAL4b', 'https://api.spotify.com/v1/albums/4TqFHsIfmRgHNB3FLL5pKI', 'https://api.spotify.com/v1/albums/6cyFbDC72hy7WWKLoGAQE9', 'https://api.spotify.com/v1/albums/5fptkh1tQob7CMGRqihha1', 'https://api.spotify.com/v1/albums/41Y2U2Oy92XK8xSN7gXmoE', 'https://api.spotify.com/v1/albums/7DTn18bcFCNls94EyPfmFe', 'https://api.spotify.com/v1/albums/4zo2ZTMFIOKSmnDOI3LGEM', 'https://api.spotify.com/v1/albums/42ZPqSxWX5C5h90Bzz6s9R', 'https://api.spotify.com/v1/albums/6rOtLJHCfotj0gpkgaQa2R', 'https://api.spotify.com/v1/albums/2tIeKOCdqLuDZMSWtuHa2B', 'https://api.spotify.com/v1/albums/4gxyr06a3BjsinB3sxrqzA', 'https://api.spotify.com/v1/albums/5hYqMXq8qMf6FKPFGxl6Sm', 'https://api.spotify.com/v1/albums/1PVjLl1Ns6JihGZv8S0vfD', 'https://api.spotify.com/v1/albums/0mEvl65Cm91K1EAIjiGfOG', 'https://api.spotify.com/v1/albums/5Qcbacw3rlqaXFpbIL5Ys6', 'https://api.spotify.com/v1/albums/1zpglRcWM6VnMkpsFkHIdt', 'https://api.spotify.com/v1/albums/1L5jwuUr0bWojNCYiHSkYY', 'https://api.spotify.com/v1/albums/2tiDmmSJuPoAp4XmibFmmY', 'https://api.spotify.com/v1/albums/2JYK4U5BKNFUQqrP8FHSTJ', 'https://api.spotify.com/v1/albums/3OYwbhCCD9bw6E5812VS6u']#interface.get_links_from_albums_list(albums_list)
# tracks_credentials = [
#     {
#       "artists": [
#         "PHARAOH"
#       ],
#       "name": "На Одну Улыбку Больше",
#       "href": "https://api.spotify.com/v1/tracks/2HFXfZb2LiHPhDwVskRNHb"
#     },
#     {
#       "artists": [
#         "PHARAOH"
#       ],
#       "name": "Лазарь",
#       "href": "https://api.spotify.com/v1/tracks/1oGoUdRZECjnB9gpYRSMpl"
#     },
#     {
#       "artists": [
#         "PHARAOH"
#       ],
#       "name": "В Прошлых Жизнях",
#       "href": "https://api.spotify.com/v1/tracks/3WGakm40Mnl5oDNmcTApLY"
#     },
# ]#interface.get_data_for_tracks(links_albums)
# # print(tracks_credentials)
# tracks_credentials = [{'artists': ['PHARAOH'], 'name': 'На Одну Улыбку Больше', 'preview_url': 'https://p.scdn.co/mp3-preview/c78c31feb43200fa91259b8934df1bdaf08ae64a?cid=d71f59d882784671888f6638ba5474fc'}, {'artists': ['PHARAOH'], 'name': 'Лазарь', 'preview_url': 'https://p.scdn.co/mp3-preview/55ccf3397d8984494fb97b0084efd94d1b8165f4?cid=d71f59d882784671888f6638ba5474fc'}, {'artists': ['PHARAOH'], 'name': 'В Прошлых Жизнях', 'preview_url': 'https://p.scdn.co/mp3-preview/ab40bc1f10b2a0e0d7ff1260f34677ce78a5b46d?cid=d71f59d882784671888f6638ba5474fc'}]#interface.get_preview_tracks(tracks_href=tracks_credentials)
# # print(tracks_credentials)

# from audio_processing.features_extraction.audio_analysis import AudioProcessing

# audio_from_url = AudioProcessing(filename="https://p.scdn.co/mp3-preview/c78c31feb43200fa91259b8934df1bdaf08ae64a?cid=d71f59d882784671888f6638ba5474fc")
# audio_from_local_installed = AudioProcessing(filename="audio_processing/tests/computing/test_audios/different/example09.mp3")

# audio_from_url.load_file(is_url=True)
# audio_from_url.set_features_base()
# audio_from_url.set_features_advanced()
# signature_url = audio_from_url.get_file_signature()

# audio_from_local_installed.load_file()
# audio_from_local_installed.set_features_base()
# audio_from_local_installed.set_features_advanced()
# signature_local_installed = audio_from_local_installed.get_file_signature()
# print(signature_local_installed == signature_url)
# interface = SpotifyApiInterface()
# json_data = interface.get_preview_tracks_from_album("41Y2U2Oy92XK8xSN7gXmoE")
# # for data in json_data:
# #     print(data)
# # print(json_data)
# tracks_preview = interface.get_clean_data_from_preview_json(json_data=json_data.get("items"))
# print(tracks_preview)