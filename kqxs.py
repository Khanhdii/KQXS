from fastapi import FastAPI
import pandas as pd
import cloudscraper
import requests
from bs4 import BeautifulSoup
from datetime import datetime

app = FastAPI()

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import cloudscraper
import pandas as pd


giai_mapping = {
    "giai8": 8,
    "giai7": 7,
    "giai6": 6,
    "giai5": 5,
    "giai4": 4,
    "giai3": 3,
    "giai2": 2,
    "giai1": 1,
    "giaidb": 0
}

headers = {"User-Agent": "Mozilla/5.0"}

def crawl_mien_nam_minh_ngoc():
    url = "https://www.xosominhngoc.com/ket-qua-xo-so/mien-nam/thu-hai.html"
    return crawl_mien_minh_ngoc(url, 3)

def crawl_mien_trung_minh_ngoc():
    url = "https://www.xosominhngoc.com/ket-qua-xo-so/mien-trung/thu-hai.html"
    return crawl_mien_minh_ngoc(url, 2)

def crawl_mien_bac_minh_ngoc():
    url = "https://www.xosominhngoc.com/ket-qua-xo-so/mien-bac/thu-hai.html"
    res = requests.get(url, headers=headers)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, "html.parser")

    title_text = soup.select_one("div.title").get_text(strip=True)
    ngay_quay_raw = title_text.split('-')[-1].strip()
    ngay_quay = datetime.strptime(ngay_quay_raw, "%d/%m/%Y").strftime("%Y-%m-%d")

    data = []
    ten_dai = "Miền Bắc"
    for giai_class, giai_so in giai_mapping.items():
        td = soup.select_one(f"td.{giai_class}")
        if td:
            numbers = [div.get_text(strip=True) for div in td.find_all("div")]
            for idx, num in enumerate(numbers, start=0):
                data.append({
                    "Ngày": ngay_quay,
                    "Đài": ten_dai,
                    "Giải": f"{giai_so}.{idx}",
                    "Minh Ngọc": num
                })

    return pd.DataFrame(data)

def crawl_mien_minh_ngoc(url, so_dai):
    res = requests.get(url, headers=headers)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, "html.parser")

    title_text = soup.select_one("div.title").get_text(strip=True)
    ngay_quay_raw = title_text.split('-')[-1].strip()
    ngay_quay = datetime.strptime(ngay_quay_raw, "%d/%m/%Y").strftime("%Y-%m-%d")

    data = []
    tables = soup.select(".rightcl")[0:so_dai]
    for table in tables:
        ten_dai = table.select_one("td.tinh a").get_text(strip=True)
        for giai_class, giai_so in giai_mapping.items():
            td = table.select_one(f"td.{giai_class}")
            if td:
                numbers = [div.get_text(strip=True) for div in td.find_all("div")]
                for idx, num in enumerate(numbers, start=0):
                    data.append({
                        "Ngày": ngay_quay,
                        "Đài": ten_dai,
                        "Giải": f"{giai_so}.{idx}",
                        "Minh Ngọc": num
                    })
    return pd.DataFrame(data)



def crawl_mien_nam_dai_phat():
    url = "https://xosodaiphat.com/xsmn-thu-2.html"
    return crawl_dai_phat(url)

def crawl_mien_trung_dai_phat():
    url = "https://xosodaiphat.com/xsmt-thu-2.html"
    return crawl_dai_phat(url)

def crawl_mien_bac_dai_phat():
    url = "https://xosodaiphat.com/xsmb-thu-2.html"
    return crawl_dai_phat(url)

def crawl_dai_phat(url):
    scraper = cloudscraper.create_scraper()
    res = scraper.get(url)
    res.encoding = 'utf-8'
    soup = BeautifulSoup(res.text, "html.parser")

    table = soup.select_one(".block-main-content")
    cells = table.find_all("td")

    giai = [span.text.strip() for span in cells[0].find_all("span") if span.text.strip().isdigit()]
    return giai


def so_sanh_ket_qua(df_minhngoc, list_daiphat, ten_mien):
    # Lấy danh sách số từ DataFrame Minh Ngọc
    list_minhngoc = df_minhngoc['Minh Ngọc'].tolist()

    # Sort cả 2 list
    list_minhngoc_sorted = sorted(list_minhngoc)
    list_daiphat_sorted = sorted(list_daiphat)

    if list_minhngoc_sorted == list_daiphat_sorted:
        print(f"Kết quả {ten_mien}: ĐÚNG ✅")
    else:
        khac_biet = []
        print(f"Kết quả {ten_mien}: SAI ❌")
        for idx, row in df_minhngoc.iterrows():
            so = row['Minh Ngọc']
            print(so)
            if so not in list_daiphat:
                khac_biet.append(f"Đài: {row['Đài']}, Giải: {row['Giải']}, Số: {so}")
        for loi in khac_biet:
            print(f"{loi}")

@app.get("/so-sanh/{mien}")
def so_sanh_mien(mien: str):
    if mien == "mien-nam":
        df_minhngoc = crawl_mien_nam_minh_ngoc()
        list_daiphat = crawl_mien_nam_dai_phat()
        ten_mien = "Miền Nam"
    elif mien == "mien-trung":
        df_minhngoc = crawl_mien_trung_minh_ngoc()
        list_daiphat = crawl_mien_trung_dai_phat()
        ten_mien = "Miền Trung"
    elif mien == "mien-bac":
        df_minhngoc = crawl_mien_bac_minh_ngoc()
        list_daiphat = crawl_mien_bac_dai_phat()
        ten_mien = "Miền Bắc"
    else:
        return {"error": "Miền không hợp lệ. Vui lòng chọn: mien-nam, mien-trung, mien-bac"}

    list_minhngoc_sorted = sorted(df_minhngoc['Minh Ngọc'].tolist())
    list_daiphat_sorted = sorted(list_daiphat)

    if list_minhngoc_sorted == list_daiphat_sorted:
        return {"mien": ten_mien, "ket_qua": "ĐÚNG ✅"}
    else:
        khac_biet = []
        for idx, row in df_minhngoc.iterrows():
            so = row['Minh Ngọc']
            if so not in list_daiphat:
                khac_biet.append({
                    "Đài": row['Đài'],
                    "Giải": row['Giải'],
                    "Số": so
                })
        return {
            "mien": ten_mien,
            "ket_qua": "SAI ❌",
            "khac_biet": khac_biet
        }
