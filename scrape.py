from os.path import isfile, join
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import vimeo_dl as vimeo
import subprocess
import time
import re
import os
import glob
import pickle
import dotenv

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_file = os.path.join(BASE_DIR, ".env")
if os.path.isfile(dotenv_file):
    dotenv.load_dotenv(dotenv_file)
urls = []


def read_urls():
    file = open('urls.txt', 'rt')
    for line in file.readlines():
        urls.append(line)


def scrape_video_url(url):
    driver = webdriver.Chrome()
    cookies = pickle.load(open("cookies.pkl", "rb"))
    for cookie in cookies:
        driver.add_cookie(cookie)

    driver.get(url)
    try:
        element = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.ID, 'vimeo-player-1'))
        )
        div = element.get_attribute('innerHTML')
        s2 = 'https://player.vimeo.com/video/'
        s3 = '?'
        url = div[div.index(s2): div.index(s3)]
        print('URL:', url)

    except Exception as err:
        print('ERROR')
        print(err)
        return None
    finally:
        driver.quit()
    return url


def get_course_and_name(url):
    s1 = os.environ.get('URL')
    s = url[len(s1):]
    s = s.split('/')
    course = os.environ.get('FILE_PATH') + s[0]
    name = s[1]
    name.strip('\n')

    entries = os.listdir(os.environ.get('FILE_PATH'))
    if s[0] not in entries:
        os.mkdir(course)
    lessons = [f for f in os.listdir(course) if isfile(join(course, f))]
    name = '%d-%s' % (len(lessons)+1, name)

    path = course + '/' + name
    os.mkdir(path=path)

    return name, path


def download_video(url, path):
    path = path.strip('\n') + '.mp4'
    url = url.strip('\n')
    print(path)
    command = 'youtube-dl "%s" --output %s' % (
        url, path)
    command = command.strip('\n')
    print(command)
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
    while True:
        output = process.stdout.readline()
        if process.poll() is not None:
            break
        if output:
            print(output.strip())
    print(process.poll())


'''
def add_id_token():
    refresh_token = 'AE0u-Nf4DaKlDdEp_XaKYBPH0QQxZKEAALGyTQ_3hQ4AeP22fco1WCVM48ij6TPqn5VEvXGArM_jKD-j16-HdXBGY-SuRpoDVYKYhMQnlU0O5DD9AuIsrr3eNsc4z4C0D77hijMLwJmUcIWXqjOWYXLrTakDBdXjLYK7JnvxnvR5kFZqIcBWpyMVjMTJzCzLZBiNy2JLf4O0bwaCupj0wrpdpnGUEuTi-Q'
    id_token = get_id(refresh_token)
'''


if __name__ == '__main__':
    read_urls()
    for url in urls:
        video_url = scrape_video_url(url)
        if video_url is not None:
            name, path = get_course_and_name(url)
            download_video(video_url, path)
        else:
            print('ERROR not found', url)
