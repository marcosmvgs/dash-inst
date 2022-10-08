from bs4 import BeautifulSoup
import re
from datetime import datetime
from SPFO import coletando_notas
import pandas as pd
import numpy as np
import AC


def main(usuario='41374373869', senha='V!toria120797'):

    fases = {'Instrumento': ['03F'],
             'Formatura Bás/Opr': ['05F'],
             'Ataque': ['34F', '34/64F'],
             'ApAA': ['36F'],
             'CAA': ['37F'],
             'Combate': ['11F'],
             'Tiro Aéreo': ['15F'],
             'Ar-Solo': ['07/08/10F'],
             'Interceptação': ['44F'],
             'Adaptação Diurna': ['01F', '01/03F'],
             'Adaptação Noturna': ['04F', '03/04F'],
             'Form IN Noturno': ['04FL'],
             'Nav Rádio': ['06F'],
             'EEXD': ['17F'],
             'PAC/Varredura': ['56/71F'],
             'Rec Arm': ['60FF'],
             'Adapt D/N (Simul)': ['01FS', '01/03FS'],
             'Escolta CSAR #3': ['39FL33'],
             'Escolta CSAR #4': ['39FL31']}

    usuario = usuario.replace(".", "")
    usuario = usuario.replace("-", "")
    usuario = str(usuario)
    htmls = coletando_notas(usuario, senha)

    col_data = []
    col_instrutor = []
    col_aluno = []
    col_subprograma = []
    col_codigo_oi = []
    col_grau = []

    for html in htmls:

        soup = BeautifulSoup(html, 'html.parser')
        expressao = re.compile("[0-99]")
        tag = soup.find_all('tr', attrs={'data-ri': expressao})
        subprograma = soup.find_all('label', attrs={'id': 'form1:j_idt57_label'})[0].text[0:6]

        for linha in tag:
            if not linha.find_all('span', attrs={'class': 'fichaParaCorrecao'}):
                if linha.find_all('td')[6].text != '':
                    if linha.find_all('td')[5].text != '':
                        # if not linha.find_all('span')[5].text[0] == 'R' and \
                        #         linha.find_all('span')[5].text[0:5] != 'Extra':

                        data = linha.find_all('span')[2].text  # data
                        data = datetime.strptime(data, '%d/%m/%Y')
                        instrutor = linha.find_all('span')[3].text.split(' -')[0]  # INSTRUTOR
                        aluno = linha.find_all('span')[4].text.split(' -')[0]  # ALUNO
                        codigo_oi = linha.find_all('span')[5].text  # CÓDIGO OI
                        grau = int(linha.find_all('span')[6].text)  # GRAU

                        col_data.append(data)
                        col_instrutor.append(instrutor)
                        col_aluno.append(aluno)
                        col_subprograma.append(subprograma)
                        col_codigo_oi.append(codigo_oi)
                        col_grau.append(grau)

            else:
                pass

    fichas = pd.DataFrame({'DATA': col_data,
                           'INSTRUTOR': col_instrutor,
                           'ALUNO': col_aluno,
                           'SUBPROGRAMA': col_subprograma,
                           'CODIGO': col_codigo_oi,
                           'GRAU': col_grau})

    for i, row in fichas.iterrows():
        for fase in fases.keys():
            for oi in fases.get(fase):
                if re.match(oi, fichas.loc[i, 'CODIGO'].split(' ')[-1]):
                    fichas.loc[i, 'FASE'] = fase

    fichas['CODIGO_PRIMEIRA'] = fichas['CODIGO'].apply(lambda x: x[0])
    conditions = [(fichas['CODIGO_PRIMEIRA'] == 'R'),
                  (fichas['CODIGO_PRIMEIRA'] == 'E'),
                  (fichas['CODIGO_PRIMEIRA'] != 'R') & (fichas['CODIGO_PRIMEIRA'] != 'E')]
    values = ['Revisão', 'Extra', 'Normal']
    fichas['TIPO'] = np.select(conditions, values)
    fichas = fichas.drop(columns=['CODIGO_PRIMEIRA'])

    columns_titles = ['DATA', 'INSTRUTOR', 'ALUNO', 'SUBPROGRAMA', 'CODIGO', 'TIPO', 'GRAU', 'FASE']
    fichas = fichas.reindex(columns=columns_titles)

    fichas.to_excel('TODAS_FICHAS.xlsx', sheet_name='marcos', index=False)


if __name__ == '__main__':
    main()
    AC.main()


