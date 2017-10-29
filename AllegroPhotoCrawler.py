import argparse
import re
from urllib import request, parse
from urllib import error


def downloadWebpage(url, values=''):
    data = parse.urlencode(values)
    req = request.Request(url + '?' + data, headers={"User-Agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"})
    response = request.urlopen(req)
    the_page = response.read()
    response.close()
    return the_page

def downloadAndSaveFile(url, directory_name, filename):
    try:
        req = request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17"})
        response = request.urlopen(req, None, 15)
        output_file = open(directory_name + '/' + str(filename) + ".jpg", 'wb')

        data = response.read()
        output_file.write(data)
        response.close();
    except IOError as ioe:  # If there is any IOError
        pass
    except error.HTTPError as e:  # If there is any HTTPError
        pass
    except error.URLError as e:
        pass
    except UnicodeEncodeError:  # Possible that we get some malformed urls because regex is not perfect :sadface:
        pass

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
        description='''Skrypt do pobierania zdjęć z aukcji allegro''',
    )
    parser.add_argument('--category', type=str, default='', help='Nazwa kategorii, z listy dostępnych na allegro')
    parser.add_argument('--phrase', type=str, default='', help='Hasło wyszukiwania')
    parser.add_argument('--output-path', type=str, default='', help='Katalog zapisywania pobranych obrazów')
    args=parser.parse_args()

    category = args.category.replace("'", "")
    phrase = args.phrase.replace("'", "")
    output_path = args.output_path.replace("'","")

    allegro_url = 'https://allegro.pl'
    allegro_url = allegro_url + '/kategoria/' + category
    directory_name = output_path + '/' + category + '_' + phrase
    createDirectory(directory_name)

    x = 1
    while True:
        if phrase != '':
            values = { 'string' : phrase,
                        'p' : x}
        else:
            values = { 'p' : x }

        webpage = downloadWebpage(allegro_url, values).decode('unicode-escape') #Allegro do linków z oryginałami obrazów stosuje kodowanie unicode z /u0000 etc.

        page_count = int(re.findall('data-maxpage="(.*?)"', webpage)[0]) #Extracts total page count returned by allegro

        m = re.findall('("https(.*?)allegroimg.com/original(.*?)")', webpage)  # Regex for url of full-sized images

        print('Links found: ' + str(len(m)))

        k = 0
        for imgurl in m:
            _url = str(imgurl[0].replace('"', ''))
            downloadAndSaveFile(_url, directory_name, 'page{0}_{1}'.format(x, k))
            k = k + 1

        print("Done page {0}".format(x))
        x = x + 1

        if (x > page_count):
            break
