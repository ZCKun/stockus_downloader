import os
import sys
import requests

from typing import Optional


download_path = './reports'
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'Host': 'api.stock.us',
    'Referer': 'https://stock.us/cn/report/quant',
    'Origin': 'https://stock.us',
    'Accept-Language': 'zh-CN',
}


def query(key: str, page: int = 1, page_size: int = 200) -> Optional[dict]:
    print(f"start search the page {page} of `{key}`", end='\r', flush=True)
    url = 'https://api.stock.us/api/v1/research/report-list'
    params = {
        'category': 8,
        'dates': 'all',
        'q': key.strip(),
        'org_name': '',
        'author': '',
        'xcf_years': '',
        'search_fields': 'title',
        'page': page,
        'page_size': page_size,
    }
    resp = requests.get(url, headers=headers, params=params)
    if resp.status_code != 200:
        print(f"query `{key}` fail, the response status code `{resp.status_code}` is invaild")
        return

    data = resp.json()
    return data


def search(key: str) -> Optional[list]:
    page_size = 100
    data = query(key, 1, page_size)
    if 'total' not in data or 'data' not in data:
        print(data)
        return

    result = data['data']
    if (total := int(data['total'])) > page_size:
        p = (total + page_size - 1) // page_size
        for page in range(2, p+1):
            data = query(key, page, page_size)
            result += data['data']

    print()
    return result


def pdf_download(item: dict) -> bool:
    report_id = item['id']
    report_title = item['title']
    url = 'https://api.stock.us/api/v1/report-file/' + report_id
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print(f"download report `{report_title}`@`{report_id}` fail, response code {resp.status_code}")
        return False
    save_path = os.path.join(download_path, f"{report_title}.pdf")
    with open(save_path, "wb") as f:
        f.write(resp.content)
    print(f"report `{report_id}` successfull saved on {save_path}")
    return True


def exit():
    print("bye :)")
    sys.exit(0)


def input_check(key: str):
    key = key.upper()
    if key in ['EXIST', 'QUIT', 'Q']:
        exit()


def app():
    key = input("Keyword: ").strip()
    if not key:
        return

    input_check(key)

    ret = search(key)
    if not ret:
        print(f"not found `{key}` result")
        return

    for i, item in enumerate(ret):
        date = item['pub_date'].split('T')[0].strip()
        org_name = item['org_name'].strip()
        title = item['title'].strip()
        print(f"[{i}]\t{date}\t{org_name}\t《{title}》")

    do_download = input(f"found {len(ret)} result, download all?[Y/N] ").strip().upper() in ['Y', 'YES']
    if do_download:
        success_count = 0
        for item in ret:
            if pdf_download(item):
                success_count += 1
        print(f"all reports download completed, success save {success_count} reports")


def setup():
    global download_path
    p = input(f"reports save path?(default:{download_path}): ").strip()
    if not p:
        return
    input_check(p)
    download_path = p
    if not os.path.exists(download_path):
        os.makedirs(download_path)


def main():
    setup()
    while True:
        app()
        print()


if __name__ == '__main__':
    main()

