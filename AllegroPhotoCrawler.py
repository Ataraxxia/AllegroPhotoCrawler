import argparse
import re
import time
import http.client
from multiprocessing.dummy import Pool
from urllib import request, parse
from urllib import error

HEADER = {"User-Agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"}

def downloadWebpage(url, values=''):
    data = parse.urlencode(values)
    print('URL: {0}'.format(url + '?' + data))
    req = request.Request(url + '?' + data, headers=HEADER)
    response = request.urlopen(req)
    the_page = response.read()
    response.close()
    return the_page

def downloadAndSaveFile(url, filename, directory_name):
    try:
        req = request.Request(url, headers=HEADER)
        response = request.urlopen(req, None, 15)
        data = response.read()

        filename = directory_name + '\\' + str(filename) + ".jpg"
        output_file = open(filename, 'wb')
        output_file.write(data)
        response.close();
    except (http.client.IncompleteRead):
        print("IncompleteRead! {0}".format(url))
    except IOError as ioe:
        print(ioe)
        print("IOError!")
    except error.HTTPError as e:
        print("HTTPError!")
    except error.URLError as e:
        print("URLError!")
    except UnicodeEncodeError:  # Possible that we get some malformed urls because regex is not perfect :sadface:
        print("UnicodeError!")


def createDirectory(name):
    import os
    try:
        os.makedirs(name)
    except OSError as e:
        if e.errno != 17:
            raise
        pass

###
#
# Kategorie:
#   motoryzacja
#       samochody-149
###

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='''Script for automated image files download from allegro website''',
    )
    parser.add_argument('--category', type=str, default='', help='Category name')
    parser.add_argument('--phrase', type=str, default='', help='Search keyword')
    parser.add_argument('--output-path', type=str, default='', help='Path to directory where files will be saved')
    parser.add_argument('--connections', type=int, default=10, help='How many requests to send in pararell')
    parser.add_argument('--pages', type=str, default='0', help='Range of pages you want to search for images specified as FirstPage,LastPage. Default settings searches all pages it can')
    args=parser.parse_args()

    category = args.category
    phrase = args.phrase
    output_path = args.output_path
    connections = args.connections
    pages_range = args.pages

    allegro_url = 'https://allegro.pl'
    allegro_url = allegro_url + '/kategoria/' + category
    directory_name = output_path + '\\' + category + '_' + phrase
    createDirectory(directory_name)

    if pages_range == '0':
        values = { }
        webpage = downloadWebpage(allegro_url, values).decode('unicode-escape') #Full-sized images have names encoded with unicode
        firstPage = 1
        lastPage = int(re.findall('data-maxpage="(.*?)"', webpage)[0])
    else:
        pages_range = pages_range.split(',')
        firstPage = int(pages_range[0])
        lastPage = int(pages_range[1])

    for p in range(firstPage, lastPage + 1):
        start_time = time.time()
        print('Starting page {0}'.format(p))
        values = { 'string' : phrase, 'p' : p}

        webpage = downloadWebpage(allegro_url, values).decode('unicode-escape')
        matches = re.findall('("https(.*?)allegroimg.com/original(.*?)")', webpage)

        print('Links found: ' + str(len(matches)))

        matches = [x[0] for x in matches]
        matches = [m.replace('"', '') for m in matches]
        file_names = ['page_' + str(p) + '_' + str(x) for x in range(len(matches) + 1)]
        prod = zip(matches, file_names, [directory_name for x in range(len(matches))])

        result = Pool(connections).starmap(downloadAndSaveFile, prod)

        print("Done page {0} in {1}min".format(p, (time.time() - start_time)/60))
