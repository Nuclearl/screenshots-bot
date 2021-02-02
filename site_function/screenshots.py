from selenium import webdriver


async def generate_photo(url, path):
    try:
        options = webdriver.FirefoxOptions()
        options.headless = True
        driver = webdriver.Firefox(options=options, executable_path='site_function/geckodriver.exe')

        driver.get(url)

        S = lambda X: driver.execute_script('return document.body.parentNode.scroll' + X)
        driver.set_window_size(S('Width'), S('Height'))  # May need manual adjustment
        driver.find_element_by_tag_name('body').screenshot(path)

        driver.quit()
        return True
    except Exception as e:
        print(e)
        return False
