from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.keys import Keys
from datetime import datetime
from time import sleep
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.proxy import Proxy, ProxyType


def acessar_sagem(usuario, senha):

    """--- Abrindo o Browser ---"""
    options = Options()
    options.headless = False
    proxy = Proxy({'proxyType': ProxyType.MANUAL,
                   'httpProxy': '10.120.32.4',
                   'noProxy': 'localhost, 127.0.0.1.10.0.0.0/8, .intraer'})
    browser = webdriver.Firefox(options=options)
    url = 'http://10.120.24.70:8080/MentorSagemWeb/principal.jsf'
    browser.get(url)

    wait = WebDriverWait(driver=browser, timeout=30)
    action = ActionChains(driver=browser)

    browser.find_elements(By.ID, 'form_id:cpf_id')[0].send_keys(usuario)
    browser.find_elements(By.ID, 'form_id:senha_id')[0].send_keys(senha)
    browser.find_element(By.ID, 'form_id:acessar_id').click()

    return browser, wait, action


def coletando_notas(usuario, senha):

    browser, wait, action = acessar_sagem(usuario, senha)

    "--- Acessando as fichas do SPFO-1"
    menu_instrucao = wait.until(ec.element_to_be_clickable((By.ID, 'menu-instrução')))
    menu_instrucao.click()

    pesq_fichas = wait.until(ec.element_to_be_clickable((By.XPATH, "//span[text()='Pesquisar Fichas']")))
    action.move_to_element(pesq_fichas).click().perform()
    wait.until(ec.invisibility_of_element_located((By.ID, "j_idt11")))

    sleep(8)
    select_esq = wait.until(ec.element_to_be_clickable((By.XPATH,
                                                        "//span[@class='ui-icon ui-icon-triangle-1-s ui-c']")))

    action.move_to_element(select_esq).click().perform()
    wait.until(ec.invisibility_of_element_located((By.ID, "j_idt11")))

    esc = wait.until(ec.element_to_be_clickable((By.XPATH, "//li[@id='form1:j_idt53_1' and text()='1/3 GAV']")))
    esc.click()
    wait.until(ec.invisibility_of_element_located((By.ID, "j_idt11")))

    select_curso = wait.until(ec.element_to_be_clickable((By.XPATH,
                                                          "//div[@id='form1:j_idt57']//span[@class='ui-icon ui-"
                                                          "icon-triangle-1-s ui-c']")))
    select_curso.click()
    wait.until(ec.invisibility_of_element_located((By.ID, "j_idt11")))

    subprogramas = browser.find_elements(By.XPATH, f'//ul[@id="form1:j_idt57_items"]//li')
    codigos = []
    for i in range(1, len(subprogramas)):
        select_curso = wait.until(ec.element_to_be_clickable((By.XPATH,
                                                              "//div[@id='form1:j_idt57']//span[@class='ui-icon ui-"
                                                              "icon-triangle-1-s ui-c']")))
        select_curso.click()

        wait.until(ec.invisibility_of_element_located((By.ID, "j_idt11")))
        try:
            subprograma_selecionado = browser.find_element(
                By.XPATH, f'//ul[@id="form1:j_idt57_items"]//li[@id="form1:j_idt57_{i}"]')
            subprograma_selecionado.click()
        except:
            select_curso = wait.until(ec.element_to_be_clickable((By.XPATH,
                                                                  "//div[@id='form1:j_idt57']//span[@class='ui-icon ui-"
                                                                  "icon-triangle-1-s ui-c']")))
            select_curso.click()

            wait.until(ec.invisibility_of_element_located((By.ID, "j_idt11")))

        wait.until(ec.invisibility_of_element_located((By.ID, "j_idt11")))

        data_inicio = wait.until(ec.presence_of_element_located((By.XPATH, "//input[@id='form1:j_idt88_input']")))
        sleep(2)
        data_inicio.click()
        data_inicio.send_keys('01012022')
        data_inicio.send_keys(Keys.TAB)
        sleep(2)

        data_final = wait.until(ec.presence_of_element_located((By.XPATH, "//input[@id='form1:j_idt90_input']")))
        hoje = datetime.now().date().strftime("%d%m%Y")
        data_final.send_keys(hoje)
        data_final.send_keys(Keys.TAB)
        sleep(2)

        pesquisar = wait.until(
            ec.element_to_be_clickable((By.XPATH, "//span[@class='ui-button-text ui-c' and text()='Pesquisar']")))
        pesquisar.click()
        try:
            wait.until(ec.invisibility_of_element_located((By.ID, "j_idt11")))
        except:
            pass

        codigo_fonte = browser.page_source
        codigos.append(codigo_fonte)

    return codigos
