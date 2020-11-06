# 🌌 artist_net 🌌
An effort to catalogue artists in an interesting visual format. Currently this is a parser for wikipedia's [list of painters by name](https://en.wikipedia.org/wiki/List_of_painters_by_name) and each corresponding painter. Now experimenting with some data mining.

# Usage
## Dependencies
Written in Python 3.7 HTML parsing is done using BeautifulSoup4, which you can install like this:
`conda install -c anaconda beautifulsoup4`

## Usage
`python web_downloader.py --download`

This will download 26 html files from wikipedia (one for each letter) and wait 7 seconds in between each one because I'm really not trying to get blocked from Wikipedia. Then it will download the page for every artist linked. If you only want the list files do:

`python web_downloader.py --download --list-only`

## Created by Lauren Sigda and Ryan Maciel
