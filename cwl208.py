import requests
from bs4 import BeautifulSoup
import csv
import re

url = "https://pakmag.net/film/db/musicUrduSongs.php"
headers = {'User-Agent': 'Mozilla/5.0'}

def scrape_songs():
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # All song entries are in tables with id='dbTable'
    tables = soup.find_all('table', id='dbTable')
    
    song_data = []
    
    for table in tables:
        div_inline = table.find('div', class_='inline')
        
        # If the div doesn't exist, this isn't a song table
        if not div_inline:
            continue 
            
        song_tag = div_inline.find('a')
        song_name = song_tag.text.strip() if song_tag else "N/A"
        
        movie_h6 = table.find('h6', class_='inline')
        movie_name = "N/A"
        release_year = "N/A"
        
        if movie_h6:
            movie_tag = movie_h6.find('a')
            movie_name = movie_tag.text.strip() if movie_tag else "N/A"
            year_match = re.search(r'(\d{4})', movie_h6.text)
            if year_match:
                release_year = year_match.group(1)

        # Some tables might not have an h6, so we add a fallback
        all_h6 = table.find_all('h6')
        details_text = all_h6[-1].text if all_h6 else ""
        
        singers = re.search(r'Singer\(s\):\s*(.*?),', details_text)
        music = re.search(r'Music:\s*(.*?),', details_text)
        poet = re.search(r'Poet:\s*(.*?),', details_text)
        actors = re.search(r'Actor\(s\):\s*(.*)', details_text)

        song_data.append({
            'Song Name': song_name,
            'Movie Name': movie_name,
            'Release Year': release_year,
            'Music Director': music.group(1).strip() if music else "N/A",
            'Poet': poet.group(1).strip() if poet else "N/A",
            'Singers': singers.group(1).strip() if singers else "N/A",
            'Actors': actors.group(1).strip() if actors else "N/A"
        })

    if not song_data:
        print("No song data was found. The website structure might have changed.")
        return

    # Save to CSV
    keys = song_data[0].keys()
    with open('pakistani_songs.csv', 'w', newline='', encoding='utf-8') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(song_data)

    print(f"Successfully scraped {len(song_data)} songs to pakistani_songs.csv")

if __name__ == "__main__":
    scrape_songs()
