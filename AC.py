import re
import time
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
import SPFO


def main(usuario='41374373869', senha='V!itoria120797'):

    # Login
    browser, wait, action = SPFO.acessar_sagem(usuario, senha)

    # Menu instrução
    menu_instrucao = wait.until(ec.element_to_be_clickable((By.ID, 'menu-instrução')))
    menu_instrucao.click()

    # Acessando o item afetivo-cognitivo
    afet_cogn = wait.until(ec.element_to_be_clickable((By.XPATH, "//span[text()='Afetivo-Cognitivo']")))
    action.move_to_element(afet_cogn).click().perform()
    wait.until(ec.invisibility_of_element_located((By.ID, "j_idt10")))

    # Selecionando esquadrão
    select_esq = wait.until(ec.element_to_be_clickable((By.XPATH,
                                                        "//span[@class='ui-icon ui-icon-triangle-1-s ui-c']")))
    action.move_to_element(select_esq).click().perform()

    esc = wait.until(ec.element_to_be_clickable((By.XPATH, "//li[@id='formAnaliseItens:j_idt44_1' "
                                                           "and text()='1/3 GAV']")))
    esc.click()
    wait.until(ec.invisibility_of_element_located((By.ID, "j_idt10")))

    # Selecionando o curso
    select_curso = wait.until(ec.element_to_be_clickable((By.XPATH,
                                                          "//div[@id='formAnaliseItens:j_idt49']//"
                                                          "span[@class='ui-icon ui-icon-triangle-1-s ui-c']")))
    select_curso.click()

    qtde_cursos = len(browser.find_elements(By.XPATH, '//div[@id="formAnaliseItens:j_idt49_panel"]//li')) - 1

    print(f'A quantidade de curso é {qtde_cursos}')

    nomes_lista = []
    subprograma_lista = []
    item_lista = []
    deficiente_lista = []
    precisa_melhorar_lista = []
    destacou_se_lista = []
    print(qtde_cursos)
    j = 1
    while j <= qtde_cursos:
        texto_subprograma = wait.until(
            ec.presence_of_element_located(
                (By.XPATH, f'//div[@id="formAnaliseItens:j_idt49_panel"]//li[@id="formAnaliseItens:j_idt49_{j}"]')
            )).text
        print(f'O subprograma que captei foi o {texto_subprograma}')

        subprograma = wait.until(
            ec.element_to_be_clickable(
                (By.XPATH, f'//div[@id="formAnaliseItens:j_idt49_panel"]//li[@id="formAnaliseItens:j_idt49_{j}"]')))

        subprograma.click()
        wait.until(ec.text_to_be_present_in_element((By.XPATH,
                                                     "//label[@id='formAnaliseItens:j_idt49_label']"),
                                                    f'{texto_subprograma}'))

        print(f'cliquei no subprograma {texto_subprograma}')

        time.sleep(2)
        try:
            wait.until(ec.invisibility_of_element_located((By.ID, "j_idt10")))
        except:
            pass

        try:
            select_alunos = wait.until(ec.presence_of_element_located((By.ID, "formAnaliseItens:alunos_label")))
            select_alunos.click()
            qtde_alunos = browser.find_elements(By.XPATH, "//ul[@id='formAnaliseItens:alunos_items']//li")

        except:
            pass

        else:
            k = 1
            while k < len(qtde_alunos):
                time.sleep(1.5)
                select_aluno = wait.until(ec.element_to_be_clickable((
                    By.XPATH, f"//li[@id='formAnaliseItens:alunos_{k}']")))

                select_aluno.click()
                try:
                    wait.until(ec.invisibility_of_element_located((By.ID, "j_idt10")))
                except:
                    pass

                time.sleep(3)
                texto_aluno = wait.until(ec.presence_of_element_located((
                    By.ID, 'formAnaliseItens:alunos_label'))).text

                if texto_aluno == 'CT CA-AV VANDRÉ':
                    nome = texto_aluno.split(' ')[-1]
                else:
                    nome = texto_aluno.split('NTE ')[-1]

                linhas = browser.find_elements(By.XPATH, "//tbody[@id='formAnaliseItens:j_idt60_data']//tr")

                for linha in linhas:
                    if not linha.text[::-1][0:5] == '0 0 0':
                        item = re.split(r"\d \d \d", linha.text)[0]
                        deficiente, precisa_melhorar, destacou_se = re.findall(r"\d", linha.text)[0:3]
                        nomes_lista.append(nome)
                        subprograma_lista.append(texto_subprograma[0:6])
                        item_lista.append(item)
                        deficiente_lista.append(deficiente)
                        precisa_melhorar_lista.append(precisa_melhorar)
                        destacou_se_lista.append(destacou_se)

                select_alunos = wait.until(ec.presence_of_element_located((By.ID, "formAnaliseItens:alunos_label")))
                select_alunos.click()

                k += 1
        finally:

            if j == qtde_cursos:
                break
            else:
                try:
                    wait.until(ec.invisibility_of_element_located((By.ID, "j_idt10")))
                except:
                    pass
                select_curso = wait.until(ec.element_to_be_clickable((
                    By.XPATH,
                    "//div[@id='formAnaliseItens:j_idt49']//"
                    "span[@class='ui-icon ui-icon-triangle-1-s ui-c']")))

                select_curso.click()

            j += 1

    df_ac = pd.DataFrame({'ALUNO': nomes_lista,
                          'SUBPROGRAMA': subprograma_lista,
                          'ITEM': item_lista,
                          'DEFICIENTE': deficiente_lista,
                          'PRECISA MELHORAR': precisa_melhorar_lista,
                          'DESTACOU-SE': destacou_se_lista})

    df_ac.to_excel('AC.xlsx', sheet_name='ac')


if __name__ == '__main__':
    main(usuario='41374373869', senha='V!toria120797')
