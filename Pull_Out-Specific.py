import sys
from bs4 import BeautifulSoup
from tqdm import tqdm

def extract_links_from_folder(input_file, folder_name, output_file):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
            soup = BeautifulSoup(content, 'html.parser')

        folder = soup.find('h3', string=folder_name)

        if not folder:
            print(f"Folder '{folder_name}' not found.")
            return

        links = folder.find_next('dl').find_all('a')

        with open(output_file, 'w', encoding='utf-8') as f:
            for link in tqdm(links, desc=f'Processing links in {folder_name}', unit='link'):
                f.write(str(link) + '\n')

        print(f'Links from folder "{folder_name}" have been saved to {output_file}.')

    except FileNotFoundError:
        print(f"Input file '{input_file}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    input_file = "D:/Documents/GitHub/Bookmarks-TO-Readme/bookmarks_5_1_23.html"
    folder_name = 'AI'
    output_file = 'AI.html'
    extract_links_from_folder(input_file, folder_name, output_file)
