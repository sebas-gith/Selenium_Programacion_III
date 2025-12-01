import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = "http://127.0.0.1:5000"

@pytest.fixture(scope="module")
def driver(driver_setup):
    return driver_setup

def ensure_login(driver):
    driver.get(BASE_URL)
    if "login" in driver.current_url:
        driver.find_element(By.ID, "user-input").send_keys("bibliotecario")
        driver.find_element(By.ID, "pass-input").send_keys("admin123")
        driver.find_element(By.ID, "login-btn").click()
        time.sleep(1)


def test_01_login_bad_creds(driver):
    driver.get(BASE_URL + "/logout")
    driver.find_element(By.ID, "user-input").send_keys("usuario_falso")
    driver.find_element(By.ID, "pass-input").send_keys("clave_falsa")
    driver.find_element(By.ID, "login-btn").click()
    time.sleep(1)
    alerta = driver.find_element(By.ID, "flash-message")
    assert "Credenciales inválidas" in alerta.text

def test_02_login_empty(driver):
    driver.get(BASE_URL + "/logout")
    driver.find_element(By.ID, "login-btn").click()
    assert "login" in driver.current_url

def test_03_login_success(driver):
    driver.get(BASE_URL + "/login")
    driver.find_element(By.ID, "user-input").send_keys("bibliotecario")
    driver.find_element(By.ID, "pass-input").send_keys("admin123")
    driver.find_element(By.ID, "login-btn").click()
    time.sleep(1)
    assert "dashboard" in driver.current_url

def test_04_create_invalid_type(driver):
    ensure_login(driver)
    driver.get(BASE_URL + "/dashboard")
    input_anio = driver.find_element(By.ID, "anio")
    input_anio.send_keys("TextoNoNumero")
    assert input_anio.get_attribute("value") == ""

def test_05_create_special_chars(driver):
    ensure_login(driver)
    driver.get(BASE_URL + "/dashboard")
    driver.find_element(By.ID, "titulo").send_keys("Libro @#$$")
    driver.find_element(By.ID, "autor").send_keys("Tester")
    driver.find_element(By.ID, "anio").send_keys("2022")
    driver.find_element(By.ID, "add-btn").click()
    time.sleep(1)
    assert "Libro @#$$" in driver.page_source

def test_06_create_happy(driver):
    ensure_login(driver)
    driver.get(BASE_URL + "/dashboard")
    driver.find_element(By.ID, "titulo").send_keys("El Principito")
    driver.find_element(By.ID, "autor").send_keys("Saint-Exupery")
    driver.find_element(By.ID, "anio").send_keys("1943")
    driver.find_element(By.ID, "add-btn").click()
    time.sleep(1)
    assert "El Principito" in driver.page_source

def test_07_year_limit_lower(driver):
    ensure_login(driver)
    driver.get(BASE_URL + "/dashboard")
    driver.find_element(By.ID, "titulo").send_keys("Muy Viejo")
    driver.find_element(By.ID, "autor").send_keys("Anon")
    driver.find_element(By.ID, "anio").send_keys("1899")
    driver.find_element(By.ID, "add-btn").click()
    time.sleep(1)
    assert "fuera de rango" in driver.page_source

def test_08_year_limit_upper(driver):
    ensure_login(driver)
    driver.get(BASE_URL + "/dashboard")
    driver.find_element(By.ID, "titulo").send_keys("Futuro")
    driver.find_element(By.ID, "autor").send_keys("Anon")
    driver.find_element(By.ID, "anio").send_keys("2026")
    driver.find_element(By.ID, "add-btn").click()
    time.sleep(1)
    assert "fuera de rango" in driver.page_source

def test_09_year_limit_valid(driver):
    ensure_login(driver)
    driver.get(BASE_URL + "/dashboard")
    driver.find_element(By.ID, "titulo").send_keys("Justo 1900")
    driver.find_element(By.ID, "autor").send_keys("Anon")
    driver.find_element(By.ID, "anio").send_keys("1900")
    driver.find_element(By.ID, "add-btn").click()
    time.sleep(1)
    assert "Justo 1900" in driver.page_source

def test_10_edit_happy(driver):
    ensure_login(driver)
    driver.find_element(By.ID, "titulo").send_keys("Libro Editame")
    driver.find_element(By.ID, "autor").send_keys("Yo")
    driver.find_element(By.ID, "anio").send_keys("2010")
    driver.find_element(By.ID, "add-btn").click()
    time.sleep(1)
    
    btns = driver.find_elements(By.CLASS_NAME, "btn-edit")
    btns[-1].click()
    
    driver.find_element(By.ID, "edit-titulo").clear()
    driver.find_element(By.ID, "edit-titulo").send_keys("YA EDITADO")
    driver.find_element(By.ID, "save-edit-btn").click()
    time.sleep(1)
    assert "YA EDITADO" in driver.page_source

def test_11_edit_empty(driver):
    ensure_login(driver)
    btns = driver.find_elements(By.CLASS_NAME, "btn-edit")
    if len(btns) > 0:
        btns[-1].click()
        time.sleep(1)
        
        driver.find_element(By.ID, "edit-titulo").clear()
        driver.find_element(By.ID, "save-edit-btn").click()
        
        
        mensaje_error = len(driver.find_elements(By.ID, "flash-message")) > 0
        url_editar = "editar" in driver.current_url
        
        assert url_editar or mensaje_error
        
        driver.get(BASE_URL + "/dashboard")
    else:
        pytest.skip("No hay libros")

def test_12_edit_limit_year(driver):
    ensure_login(driver)
    btns = driver.find_elements(By.CLASS_NAME, "btn-edit")
    if len(btns) > 0:
        btns[-1].click()
        driver.find_element(By.ID, "edit-anio").clear()
        driver.find_element(By.ID, "edit-anio").send_keys("3000")
        driver.find_element(By.ID, "save-edit-btn").click()
        time.sleep(1)
        assert driver.current_url != BASE_URL + "/error"
    else:
        pytest.skip("No hay libros")

def test_13_delete_count(driver):
    ensure_login(driver)
    driver.find_element(By.ID, "titulo").send_keys("Para Borrar")
    driver.find_element(By.ID, "autor").send_keys("X")
    driver.find_element(By.ID, "anio").send_keys("2020")
    driver.find_element(By.ID, "add-btn").click()
    time.sleep(1)
    
    filas_antes = len(driver.find_elements(By.CSS_SELECTOR, "#tabla-libros tbody tr"))
    
    btns = driver.find_elements(By.CLASS_NAME, "btn-delete")
    btns[-1].click()
    time.sleep(1)
    
    filas_despues = len(driver.find_elements(By.CSS_SELECTOR, "#tabla-libros tbody tr"))
    assert filas_despues == filas_antes - 1

def test_14_delete_msg(driver):
    ensure_login(driver)
    driver.find_element(By.ID, "titulo").send_keys("Msg Check")
    driver.find_element(By.ID, "autor").send_keys("X")
    driver.find_element(By.ID, "anio").send_keys("2020")
    driver.find_element(By.ID, "add-btn").click()
    time.sleep(1)
    
    btns = driver.find_elements(By.CLASS_NAME, "btn-delete")
    btns[-1].click()
    
    alerta = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.ID, "flash-message"))
    )
    assert "Libro eliminado" in alerta.text

def test_15_delete_not_found(driver):
    ensure_login(driver)
    driver.get(BASE_URL + "/eliminar/999999")
    assert "Not Found" in driver.page_source or "404" in driver.title