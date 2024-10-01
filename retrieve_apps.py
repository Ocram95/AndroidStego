import requests
from bs4 import BeautifulSoup

def find_apps_GP():
	# Google Play Store URL (Italian)
	url = "https://play.google.com/store/apps?hl=en"
	# Make a request to the website
	headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
	response = requests.get(url, headers=headers)
	# Parse the content using BeautifulSoup
	soup = BeautifulSoup(response.content, "html.parser")
	# Find the app titles (adjust the class name according to the structure of the page)
	app_titles = soup.find_all('div', class_='Epkrse')
	# Extract and print the names of the apps
	apps = []
	for app in app_titles:
		apps.append(app.text)
	return apps
	
apps = find_apps_GP()
print(apps)
		
