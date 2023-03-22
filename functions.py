from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.webdriver.common.action_chains import ActionChains

import requests

import sys
import io
from PIL import Image
from datetime import datetime as dt

import time
import threading


class KThread(threading.Thread):
    """A subclass of threading.Thread, with a kill() method.

    Come from:
    Kill a thread in Python:
    http://mail.python.org/pipermail/python-list/2004-May/260937.html
    """

    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        self.killed = False
        self.__run_backup = None

    def start(self):
        """Start the thread."""
        self.__run_backup = self.run
        self.run = self.__run  # Force the Thread to install our trace.
        threading.Thread.start(self)

    def __run(self):
        """Hacked run function, which installs the trace."""
        sys.settrace(self.globaltrace)
        self.__run_backup()
        self.run = self.__run_backup

    def globaltrace(self, frame, why, arg):
        if why == 'call':
            return self.localtrace
        return None

    def localtrace(self, frame, why, arg):
        if self.killed:
            if why == 'line':
                raise SystemExit()
        return self.localtrace

    def kill(self):
        self.killed = True


class TIMEOUT_EXCEPTION(Exception):
    """function run timeout"""
    pass


def timeout(seconds):
    def timeout_decorator(func):

        def _new_func(oldfunc, result, oldfunc_args, oldfunc_kwargs):
            result.append(oldfunc(*oldfunc_args, **oldfunc_kwargs))

        def _(*args, **kwargs):
            result = []
            new_kwargs = {
                # create new args for _new_func, because we want to get the
                # func return val to result list
                'oldfunc': func,
                'result': result,
                'oldfunc_args': args,
                'oldfunc_kwargs': kwargs
            }

            thd = KThread(target=_new_func, args=(), kwargs=new_kwargs)
            thd.start()
            thd.join(seconds)
            alive = thd.isAlive()
            thd.kill()  # kill the child thread

            if alive:
                raise TIMEOUT_EXCEPTION(
                    'function run too long, timeout %d seconds.' % seconds)
            else:
                if result:
                    return result[0]
                return result

        _.__name__ = func.__name__
        _.__doc__ = func.__doc__
        return _

    return timeout_decorator


def scroll_down(driver, delay):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(delay)


def get_images_from_charancha(driver, delay, max_images, url, down_path):
    url = url
    driver.get(url)

    original_window = driver.current_window_handle

    # Check we don't have other windows open already
    assert len(driver.window_handles) == 1

    image_urls = set()
    skips = 0
    for _ in range(20):
        for i in range(2, 11):
            driver.switch_to.window(original_window)
            driver.find_element(By.XPATH, f'//*[@id="contents2"]/div[3]/a[{i}]').click()


            thumbnails = driver.find_elements(By.CLASS_NAME, "cars__photo")

            for img in thumbnails:    #[len(image_urls) + skips:max_images]
                try:
                    img.click()
                    time.sleep(delay)
                except:
                    continue

            # Loop through until we find a new window handle
            for window_handle in driver.window_handles:
                if window_handle != original_window:
                    driver.switch_to.window(window_handle)

                    images = driver.find_elements(By.CLASS_NAME, "gallery-img")

                    for image in images[:4]:    #image = images[0]
                        if image.get_attribute('src') in image_urls:
                            max_images += 1
                            skips += 1
                            break

                        is_src = image.get_attribute('src') and 'http' in image.get_attribute('src')
                        # time.sleep(delay)

                        if is_src:
                            image_urls.add(image.get_attribute('src'))
                            try:
                                download_image(down_path, url=image.get_attribute('src'),
                                               file_name=str(len(image_urls)) + '.png',
                                               image_type='PNG', verbose=True)
                            except:
                                break
                        print(f"Found {len(image_urls)}")
                    driver.close()

        driver.switch_to.window(original_window)
        driver.find_element(By.CLASS_NAME, 'next').click()

    return image_urls


def get_images_from_chachacha(driver, delay, max_images, down_path):

    driver.get("https://www.bobaedream.co.kr/cyber/CyberCar.php?sel_m_gubun=ALL")

    url = driver.current_url
    driver.get(url)
    driver.find_element(By.XPATH, '//*[@id="content"]/div[2]/div/div[2]/div[1]/div[2]/div/div[3]/div[10]/h3/a').click()
    btn = driver.find_element(By.XPATH, '//*[@id="content"]/div[2]/div/div[2]/div[1]/div[2]/div/div[3]/div[10]/div/div[8]/span[1]/label/span')
    actions = ActionChains(driver)
    actions.move_to_element(btn).click().perform()

    original_window = driver.current_window_handle

    # Check we don't have other windows open already
    assert len(driver.window_handles) == 1

    image_urls = set()
    skips = 0
    for i in range(1, 11):
        driver.switch_to.window(original_window)
        bnt = driver.find_element(By.XPATH, f'//*[@id="content"]/div[2]/div/div[2]/div[2]/div[3]/div[5]/a[{i}]')
        actions = ActionChains(driver)
        actions.move_to_element(btn).click().perform()

        for j in range(0, 31):
            # print(j)
            img = driver.find_elements(By.CLASS_NAME, 'tit')[j]
            actions = ActionChains(driver)
            actions.move_to_element(img).click().perform()

        # Loop through until we find a new window handle
        for window_handle in driver.window_handles:
            if window_handle != original_window:
                driver.switch_to.window(window_handle)

                images = driver.find_elements(By.CLASS_NAME, "slide-img__link")

                for image in images[1:4]:    #image = images[0]
                    if image.get_attribute('href') in image_urls:
                        max_images += 1
                        skips += 1
                        break

                    is_src = image.get_attribute('href') and 'http' in image.get_attribute('href')
                    # time.sleep(delay)

                    if is_src:
                        image_urls.add(image.get_attribute('href'))
                        try:
                            download_image(down_path, url=image.get_attribute('href'),
                                           file_name=str(len(image_urls)) + '.png',
                                           image_type='PNG', verbose=True)
                        except:
                            break
                    print(f"Found {len(image_urls)}")
                driver.close()


    return image_urls


def get_images_from_bobae(driver, delay, max_images, down_path):
    driver.get("https://www.bobaedream.co.kr/cyber/CyberCar.php?sel_m_gubun=ALL&page=31&order=S11&view_size=70")
    url = driver.current_url
    driver.get(url)

    original_window = driver.current_window_handle

    # Check we don't have other windows open already
    assert len(driver.window_handles) == 1

    image_urls = set()
    for k in range(1, 1891):
        image_urls.add(str(k))
    skips = 0

    for _ in range(10):
        for i in range(3, 12):
            driver.switch_to.window(original_window)
            time.sleep(delay)
            bnt = driver.find_element(By.XPATH, f'//*[@id="listCont"]/div[2]/div/a[{i}]')
            actions = ActionChains(driver, duration=5000)
            actions.move_to_element(bnt).click().perform()
            time.sleep(delay)

            thumbnails = driver.find_elements(By.CLASS_NAME, "img.w132")

            for img in thumbnails:    #[len(image_urls) + skips:max_images]
                try:
                    img.click()
                    # time.sleep(delay)
                except:
                    continue

            # Loop through until we find a new window handle
            for window_handle in driver.window_handles:
                if window_handle != original_window:
                    driver.switch_to.window(window_handle)

                    images = []
                    for idx in range(1, 4):
                        image = driver.find_element(By.XPATH, f'//*[@id="imgPos"]/li[{idx}]/a/img')
                        images.append(image)

                    for image in images:  # image = images[0]
                        if image.get_attribute('src') in image_urls:
                            max_images += 1
                            skips += 1
                            break

                        is_src = image.get_attribute('src')  # and 'http'
                        # time.sleep(delay)

                        if is_src:
                            image_urls.add(image.get_attribute('src'))
                            try:
                                download_image(down_path, url=image.get_attribute('src'),
                                               file_name=str(len(image_urls)) + '.png',
                                               image_type='PNG', verbose=True)
                            except:
                                break
                        print(f"Found {len(image_urls)}")
                    driver.close()
        driver.switch_to.window(original_window)
        driver.find_element(By.CLASS_NAME, "next").click()

    return image_urls


@timeout(20)
def download_image(down_path, url, file_name, image_type='PNG', verbose=True):
    try:
        time = dt.now()
        curr_time = time.strftime('%H:%M:%S')
        # Content of the image will be a url
        img_content = requests.get(url).content
        # Get the bytes IO of the image
        img_file = io.BytesIO(img_content)
        # Stores the file in memory and convert to image file using Pillow
        image = Image.open(img_file)
        file_pth = down_path + file_name
        file_pth = down_path + file_name

        with open(file_pth, 'wb') as file:
            image.save(file, image_type)

        if verbose == True:
            print(f'The image: {file_pth} downloaded successfully at {curr_time}.')
    except Exception as e:
        print(f'Unable to download image from Google Photos due to\n: {str(e)}')
