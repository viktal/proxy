import requests
from multiprocessing import Pool
import config


def parse_url(url: str) -> str:
    parse = url.split('//')
    if len(parse) > 1:
        parse = parse[1]
    else:
        parse = parse[0]
    return f'https://{parse.split("/")[0]}'


def read_file():
    path = []
    with open('dicc.txt', 'r') as f:
        for item in f:
            item = item.split('\n')[0]
            path.append(item)
    return path


def check_response_code(path, site):
    url = f"{site}/{path}"
    response = requests.get(url, allow_redirects=False)
    if response.status_code != 404:
        # print(f'Code: {response.status_code} Url: {url}')
        return {'code': response.status_code, 'url': url}
    return


def dibuster(site):
    site = parse_url(site)
    response = requests.get(site)
    # if response.status_code != 200:
    #     return f'Url {site} get status code {response.status_code}'

    path = read_file()
    with Pool(processes=config.COUNT_CPU*config.COUNT_CPU) as pool:
        result = pool.starmap(check_response_code, [(e, site) for e in path])
        return result


if __name__ == "__main__":
    dibuster('auth.mail.ru')
