import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import csv


def pretvori_v_cm(text):
    besede = text.split("-")
    return round(float(besede[0]) * 30.48 + float(besede[1]) * 2.54)


def pretvori_v_kg(text):
    return round(int(text[:-2]) * 0.45359237)


filename = "defensive2.csv"
f = open(filename, "w", encoding="utf-8", newline='')
writer = csv.writer(f)
header = "leto," + "rank," + "player," + "starost," + "ekipa," + "first," + "pts_won," + "pts_max," + "share," + \
    "g," + "mp," + "pts," + "trb," + "ast," + \
    "stl," + "blk," + "fg%,"+ "ws," + "ws/48," + "defense_rank," + "height," + "weight," + \
    "wins," + "dws," + "dbpm," + "bpm," + "vorp \n"

f.write(header)

for n in range(1983, 2021):
    url = "https://www.basketball-reference.com/awards/awards_" + \
        str(n) + ".html"

    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    tabela = soup.find("table", {"id": "dpoy"}).find_all("tbody")[0]
    vrstice = tabela.find_all("tr")

    for x in range(0, 20):
        try:
            row_data = []
            columns = vrstice[x].find_all("td")
            row_data.append(str(n))
            row_data.append(str(x+1))

            for y in range(0, 15):
                row_data.append(columns[y].get_text())
            row_data.append(columns[18].get_text())
            row_data.append(columns[19].get_text())
            player_site = columns[0].find("a")["href"]

            # to get the height and weight of the players
            browser = webdriver.Firefox(options=options)
            browser.get(
                "https://www.basketball-reference.com/" + player_site)
            soup_player = BeautifulSoup(browser.page_source, 'html.parser')

            height = pretvori_v_cm(soup_player.select('span[itemprop="height"]')[
                0].get_text())
            weight = pretvori_v_kg(soup_player.select('span[itemprop="weight"]')[
                0].get_text())
            row_data.append(height)
            row_data.append(weight)
            browser.close()

            # to get advanced stats of every player
            url_koncnica = columns[2].next['href']
            browser2 = webdriver.Firefox(options=options)
            browser2.get("https://www.basketball-reference.com" + url_koncnica)
            soup2 = BeautifulSoup(browser2.page_source, 'html.parser')
            wins = soup2.find(lambda tag: tag.name ==
                               "p" and "Finished" in tag.text).get_text()[20:22]
            rank_defensive = soup2.find(
                lambda tag: tag.name == "p" and "Def Rtg" in tag.text).get_text().split('(', 2)[2][:2]
            if rank_defensive[1].isalpha():
                row_data.append(rank_defensive[0])
                row_data.append(wins)
            else:
                row_data.append(rank_defensive)
                row_data.append(wins)

            tabela = soup2.find(
                "table", {"id": "advanced"}).find_all("tbody")[0]
            player = tabela.find("td", {"csk": columns[0]['csk']})
            dws = player.parent.find("td", {"data-stat": "dws"}).get_text()
            dbpm = player.parent.find("td", {"data-stat": "dbpm"}).get_text()
            bpm = player.parent.find("td", {"data-stat": "bpm"}).get_text()
            vorp = player.parent.find("td", {"data-stat": "vorp"}).get_text()
            ws = player.parent.find("td", {"data-stat": "ws"}).get_text()
            row_data.append(dws)
            row_data.append(dbpm)
            row_data.append(bpm)
            row_data.append(vorp)
            browser2.close()
        except:
            break

        writer.writerow(row_data)

    driver.close()

f.close()
