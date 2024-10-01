import requests
from bs4 import BeautifulSoup
import os


APK_MIRROR_URL = "https://www.apkmirror.com"

# Function to make the request and parse the search results page
def get_latest_apk_links(app_name):
	headers = {'User-Agent': 'My User Agent 1.0','From': 'youremail@domain.example'}
	try:
		search_url_apk = f"{APK_MIRROR_URL}/?post_type=app_release&searchtype=apk&s={app_name.replace(' ', '+')}&bundles[]=apkm_bundles&bundles[]=apk_files"
		print("[+] Search apk: ", search_url_apk)
		response_apk = requests.get(search_url_apk, headers=headers)
		soup = BeautifulSoup(response_apk.text, "html.parser")
		#apks already sorted by publish date, so take the one with "N variants" meaning it contains at least one href to download
		releases = soup.find_all("div", class_="appRowVariantTag wrapText") #take the link
		for release in releases:
			# Filter out the ones that also have 'accent_border' in their class list
			if "accent_border" not in release.get('class', []):
				last_release_link = APK_MIRROR_URL + release.find('a')['href']
				#no need to sort by date, already sorted by page hence first occurrence
				break
		print("[+] Last Release: ", last_release_link)
		response_release = requests.get(last_release_link, headers=headers)
		soup = BeautifulSoup(response_release.text, "html.parser")
		architectures = soup.find_all("div", class_="table-row headerFont")
		#select the architectures we want to download
		arch_list = ["armeabi-v7a", "arm64-v8a", "x86", "x86_64"]
		for architecture in architectures:
			arch = next((arch for arch in arch_list if architecture.find('div', text=arch)), None)
			if arch:
				href_tag = architecture.find('a', class_='accent_color')
				if href_tag:
					#take the link and visit it
					url_download = APK_MIRROR_URL + href_tag['href']				
					response_download = requests.get(url_download, headers=headers)
					soup = BeautifulSoup(response_download.text, "html.parser")
					#take the URL of the download button
					dwd = soup.find_all("a", class_="accent_bg")
					download_link = APK_MIRROR_URL + dwd[0]['href']
					print("[+] Download link: ", download_link)
					response_download = requests.get(download_link, headers=headers)
					soup = BeautifulSoup(response_download.text, "html.parser")
					dwd = soup.find("a", {"id": "download-link"})
					print("[+] D link: ", APK_MIRROR_URL + dwd['href'])
					apk_raw = requests.get(APK_MIRROR_URL + dwd['href'], headers=headers)
					# print(apk_raw.content)
					filename = app_name + '_' + arch + '.apk'
					with open(f'/mnt/FileSources/APK_Stego/{filename}', 'wb') as file:
						file.write(apk_raw.content)
				break
	except UnboundLocalError as e:
		print("ERROR: ", e)
		get_latest_apk_links(app_name)

done_apks = os.listdir('/mnt/FileSources/APK_Stego/')
for i, app in enumerate(done_apks):
    done_apks[i] = app.split('_')[0]

with open('apps_name.txt', 'r') as file:
    apps = file.read().split('\n')

# print(apps)
for app in apps[:-1]:
    if app not in done_apks:
        print("[+] Downloading: ", app)
        apk_links = get_latest_apk_links(app)
