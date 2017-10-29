import argparse
import re
import time
from multiprocessing.dummy import Pool # use threads for I/O bound tasks
from urllib import request, parse
from urllib import error


def downloadWebpage(url, values=''):
    data = parse.urlencode(values)
    req = request.Request(url + '?' + data, headers={"User-Agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"})
    response = request.urlopen(req)
    the_page = response.read()
    response.close()
    return the_page

def downloadAndSaveFile(url, filename, directory_name):
    try:
        req = request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"})
        response = request.urlopen(req, None, 15)

        filename = directory_name + '\\' + str(filename) + ".jpg"
        output_file = open(filename, 'wb')

        data = response.read()
        output_file.write(data)
        response.close();
    except IOError as ioe:  # If there is any IOError
        print(ioe)
        print("IOError!")
    except error.HTTPError as e:  # If there is any HTTPError
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
    parser.add_argument('--connections' type=int, default=10, help='How many requests to send in pararell')
    args=parser.parse_args()

    category = args.category.replace("'", "")
    phrase = args.phrase.replace("'", "")
    output_path = args.output_path.replace("'","")
    connections = args.connections

    allegro_url = 'https://allegro.pl'
    allegro_url = allegro_url + '/kategoria/' + category
    directory_name = output_path + '\\' + category + '_' + phrase
    createDirectory(directory_name)



    p = 1
    while True:
        start_time = time.time()

        if phrase != '':
            values = { 'string' : phrase,
                        'p' : p}
        else:
            values = { 'p' : p }

        webpage = downloadWebpage(allegro_url, values).decode('unicode-escape') #Full-sized images have names encoded with unicode

        page_count = int(re.findall('data-maxpage="(.*?)"', webpage)[0])

        matches = re.findall('("https(.*?)allegroimg.com/original(.*?)")', webpage)  # Regex dla url z obrazkami w pełnym rozmiarze

        print('Links found: ' + str(len(matches)))

        matches = [x[0] for x in matches]
        matches = [m.replace('"', '') for m in matches]
        file_names = ['page_' + str(p) + '_' + str(x) for x in range(len(matches) + 1)]
        prod = zip(matches, file_names, [directory_name for x in range(len(matches))])

        result = Pool(connections).starmap(downloadAndSaveFile, prod)

        print("Done page {0} in {1}".format(p, time.time() - start_time))
        p = p + 1

        if (p > page_count):
            break
