import requests
from bs4 import BeautifulSoup
import zipfile

BASE_URL = "https://evroplast.ru/"

PRODUCT_PAGES_TYPES = ['karnizy', 'antablementy/karnizi']


def getSoupObj(link):
    return BeautifulSoup(requests.get(BASE_URL + link).text, 'html.parser')


def getCategories(soup):
    category_parent = soup.find("div", attrs={"data-type": "category-show"})
    if category_parent is None:
        return

    category_parent = category_parent.findAll("li")

    return list(map(lambda x: x.find("a")["href"][1:], category_parent))


# check product existence

def getProducts(soup):
    def linkExist(y):
        if y.find("a") is None:
            return ""
        return y.find("a")["href"]

    links = soup.findAll("div", class_="e-new-catalogue-item")
    if links is None:
        return []

    return list(map(linkExist, links))
def getPages(soup):
    if soup.find("div", class_="e-new-pag") is None:
        return 1
    return int(soup.find("div", class_="e-new-pag")["data-items"]) // 8


def goThroughPages(category):
    for i in range(1, getPages(getSoupObj(category))+2):
        soup = getSoupObj(f"{category}/?page={i}")
        if soup.find("div", class_="e-new-catalogue-item") is not None:
            for product in getProducts(soup):
                download_files(product)

def goThroughCategories(categories, page):
    if categories is None:
        categories = [page]
    for cat in categories:
        goThroughPages(cat)
        print("Category: " + cat)


def download_files(link):
    soup = getSoupObj(link)
    prodInfoParent = soup.find("div", class_="prod-params-tabs")
    title = soup.find("div", class_="prod-info-main").find("h1").text.strip()

    intructionLink = prodInfoParent.find("div", class_="param-tab-manual").find("a")["href"][1:]

    modelsLinks = []
    for modelType in prodInfoParent.find("div", class_="param-tab-models").findAll("a"):
        modelsLinks.append(modelType["href"][1:])

    with zipfile.ZipFile("instructions.zip", mode="a") as archive:
        archive.writestr(title + ".pdf", requests.get(BASE_URL + intructionLink ).content)

    with zipfile.ZipFile("models.zip", mode="a") as archive:
        archive.mkdir(title)
        for (i, model) in enumerate(modelsLinks):
            fileBytes = requests.get(BASE_URL + model)
            ext = model.split(".")[-1]
            archive.writestr(f"{title}/{i}.{ext.lower()}", fileBytes.content)
    print("downloaded: " + title)

if __name__ == "__main__":
    for page in PRODUCT_PAGES_TYPES:
        goThroughCategories(getCategories(getSoupObj(page)), page)
