#!/usr/bin/python3

import os
import requests
from pysondb import db as database
from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup


# Constants 
LOCATION = "ca"
URL = "https://peapix.com/bing/" + LOCATION


IMG_DIR = ("/images")
DB_DIR = ("/.bing-wallpaper")
DB_FILE = ("/db.json")
HOME_DIR = str(Path.home())

FULL_DB_DIR_PATH = HOME_DIR + DB_DIR
FULL_IMG_DIR_PATH = FULL_DB_DIR_PATH + IMG_DIR
FULL_DB_FILE_PATH = FULL_DB_DIR_PATH + DB_FILE


# Functions

def get_images():
	page = requests.get(URL)
	soup = BeautifulSoup(page.content, "html.parser")
	images = soup.find_all("div", class_="image-list__container")

	# Get DB
	db = database.getDb(FULL_DB_FILE_PATH)

	for image in images:

		title_element = image.find("h4", class_="image-list__title")
		date_element  = image.find("span", class_="text-gray")
		url_element   = image.find("div", class_="image-list__picture")

		title = title_element.text.strip()
		date  = datetime.strptime(date_element.text.strip(), '%B %d, %Y').strftime('%Y-%m-%d')
		url   = url_element['data-bgset'].strip().replace("_480", "")

		if not db.getBy({"date":date}):
			print("Adding entry for ",date,"...")
			db.add({"title":title, "date": date,"location": LOCATION ,"url":url})
		

def create_db_folder():
	# If "bing-wallpaper" folder doesn't exist, then create it.
	if not os.path.isdir(FULL_DB_DIR_PATH):
	    os.makedirs(FULL_DB_DIR_PATH)
	    print("created folder : ", FULL_DB_DIR_PATH)
	else:
	    print(FULL_DB_DIR_PATH, "folder already exists.")

	# If "image" folder doesn't exist, then create it.
	if not os.path.isdir(FULL_IMG_DIR_PATH):
	    os.makedirs(FULL_IMG_DIR_PATH)
	    print("created folder : ", FULL_IMG_DIR_PATH)
	else:
	    print(FULL_IMG_DIR_PATH, "folder already exists.")

def create_db_file():
	if os.path.exists(FULL_DB_FILE_PATH):
		if os.path.isfile(FULL_DB_FILE_PATH):
			print("file already exists.")
	else:
		print("created file : ", FULL_DB_FILE_PATH)
		open(FULL_DB_FILE_PATH,"w").close()

def update_wallpaper():
	# Get DB
	db = database.getDb(FULL_DB_FILE_PATH)
	date  = datetime.now().strftime('%Y-%m-%d')
	
	record = db.getBy({"date":date})
	if not record:
		print("Faild to set wallpaper...")
	else:
		
		print("Downloading the wallpaper....")
		record = record[0]
		print("Title",record['title'])
		print("Date",record['date'])

		IMG = FULL_IMG_DIR_PATH+"/"+date+"_"+LOCATION+".jpg"

		# Download the Wallpaper is not exists
		if not os.path.exists(IMG):
			downloaded_obj = requests.get(record['url'])
			with open(IMG, "wb") as file:
				file.write(downloaded_obj.content)

		print("Setting up the wallpaper....")

		# Only Works on GNOME
		os.system("gsettings set org.gnome.desktop.background picture-uri file:///"+IMG)

		print("Wallpaper setup successfully ....")

def main():
	create_db_folder()
	# create_db_file() not required anymore
	get_images()
	update_wallpaper()

if __name__ == "__main__":
    main()