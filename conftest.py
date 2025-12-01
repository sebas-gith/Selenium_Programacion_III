import pytest
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

driver = None

@pytest.fixture(scope="module")
def driver_setup():
    global driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.maximize_window()
    driver.implicitly_wait(4)
    yield driver
    driver.quit()

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    pytest_html = item.config.pluginmanager.getplugin('html')
    outcome = yield
    report = outcome.get_result()
    extra = getattr(report, 'extra', [])

    if report.when == 'call':
        if driver:
            timestamp = datetime.now().strftime('%H-%M-%S')
            filename = f"screenshot-{item.name}-{timestamp}.png"
            
            if not os.path.exists("screenshots"):
                os.makedirs("screenshots")
            path = os.path.join("screenshots", filename)
            driver.save_screenshot(path)
            
            html = f'<div><img src="screenshots/{filename}" alt="screenshot" style="width:600px;height:auto;" onclick="window.open(this.src)" align="right"/></div>'
            extra.append(pytest_html.extras.html(html))
        
        report.extra = extra