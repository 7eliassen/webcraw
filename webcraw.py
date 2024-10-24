import requests
from bs4 import BeautifulSoup
import argparse
from fake_useragent import UserAgent
from sys import exit
from rich.console import Console


def main():
    console = Console()
    args = argparse.ArgumentParser()
    args.add_argument('-u', '--url', type=str, help='url to scan', required=True)
    args.add_argument('-o', '--output', type=str, help='output file', default=False)
    args.add_argument('-s', '--silent', action='store_true', help='silent mode', default=False)
    args.add_argument('-g', '--only-good', action='store_true', help='only show good links', default=False)
    args = args.parse_args()

    ua = UserAgent()
    random_ua = ua.random
    if not args.silent:
        hello(console)

    headers = {
        "User-Agent": random_ua
    }

    url = refactor_url(args.url)
    if not args.silent:
        print_info(console, f"URL: {url}")
    result = parse(url, headers)
    if result is None:
        print_error(console, f'Invalid URL {url}')
        exit(1)

    host = find_host(url)
    if not args.silent:
        print_info(console, f"Host: {host}")
        print_info(console, f"Fake User-Agent: {headers["User-Agent"]}")
    queue = [url]
    links_ = []
    other_links = []
    visited = {}

    try:
        while queue:
            current_page = queue.pop(0)
            if current_page not in list(visited.keys()):
                response = parse(current_page, headers)
                visited[current_page] = None
                if response is None:
                    print_error(console, current_page)
                else:
                    links_.append(current_page)
                    print_success(console, current_page)
                    soup = BeautifulSoup(response, 'html.parser')
                    links = soup.find_all('a')
                    for link_ in links:
                        try:
                            link = link_['href']
                            while link.startswith('/'):
                                link = link[1:]
                            if not link.startswith('http') and not link.startswith('www.'):
                                link = refactor_link(link, url)
                            if host not in link:
                                if link not in list(visited.keys()):
                                    other_links.append(link)
                                    visited[link] = None
                                    if not args.only_good:
                                        print_info(console, link)
                            else:
                                if link not in list(visited.keys()):
                                    queue.append(link)
                        except KeyError:
                            link_ = str(link_).replace('\n', '').strip()
                            if not args.only_good:
                                print_error(console, f"{link_} has no href")
    except KeyboardInterrupt:
        print_info(console, "Program terminated by user\n")

    if args.output:
        links_arr = []
        links_arr.extend(list(set(links_)))
        with open(args.output, 'w') as f:
            for link in list(set(links_arr)):
                f.write(link + '\n')
        with open(f'other_{args.output}', 'w') as f:
            for link in other_links:
                f.write(link + '\n')


def parse(url: str, headers: dict):
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        else:
            return None
    except requests.exceptions.RequestException:
        return None


def find_host(url: str) -> str:
    url = url.replace('https://', '')
    url = url.replace('http://', '')
    return url.split('/')[0]


def refactor_url(url: str) -> str:
    url = url.strip()
    while url[-1] == '/' and url[-2] == '/':
        url = url[:-1]
    if url[-1] != '/':
        url = url + '/'
    if not url.startswith("http"):
        url = f"http://{url}"
    return url


def refactor_link(link: str, url: str) -> str:
    if url not in link:
        link = url + link
    return link


def print_error(console, message: str) -> None:
    console.print(f"[-] {message}", style="bold red")


def print_success(console, message: str) -> None:
    console.print(f"[+] {message}", style="bold green")


def print_info(console, message: str) -> None:
    console.print(f"[?] {message}", style="bold yellow")


hello_text = r'''
 .----------------.  .----------------.  .----------------.  .----------------.  .----------------.  .----------------.  .----------------. 
| .--------------. || .--------------. || .--------------. || .--------------. || .--------------. || .--------------. || .--------------. |
| | _____  _____ | || |  _________   | || |   ______     | || |     ______   | || |  _______     | || |      __      | || | _____  _____ | |
| ||_   _||_   _|| || | |_   ___  |  | || |  |_   _ \    | || |   .' ___  |  | || | |_   __ \    | || |     /  \     | || ||_   _||_   _|| |
| |  | | /\ | |  | || |   | |_  \_|  | || |    | |_) |   | || |  / .'   \_|  | || |   | |__) |   | || |    / /\ \    | || |  | | /\ | |  | |
| |  | |/  \| |  | || |   |  _|  _   | || |    |  __'.   | || |  | |         | || |   |  __ /    | || |   / ____ \   | || |  | |/  \| |  | |
| |  |   /\   |  | || |  _| |___/ |  | || |   _| |__) |  | || |  \ `.___.'\  | || |  _| |  \ \_  | || | _/ /    \ \_ | || |  |   /\   |  | |
| |  |__/  \__|  | || | |_________|  | || |  |_______/   | || |   `._____.'  | || | |____| |___| | || ||____|  |____|| || |  |__/  \__|  | |
| |              | || |              | || |              | || |              | || |              | || |              | || |              | |
| '--------------' || '--------------' || '--------------' || '--------------' || '--------------' || '--------------' || '--------------' |
 '----------------'  '----------------'  '----------------'  '----------------'  '----------------'  '----------------'  '----------------' 
 '''


def hello(console):
    console.print(f"[yellow]{hello_text}made by 7eliassen[/yellow]\n")


if __name__ == '__main__':
    main()
