import os.path

import pandas as pd
import streamlit as st


def load_te(url, sheet_name):
    data = pd.read_excel(url, sheet_name=sheet_name)
    data['BAND PRINCIPAL'] = data['BAND PRINCIPAL'].str.replace('-', '')
    data['BAND AUXILIAR'] = data['BAND AUXILIAR'].str.replace('-', '')
    data['DISTÂNCIA REAL (M)'] = data['DISTÂNCIA REAL (M)'].str.replace('-', '')
    data['DIREÇÃO (H)'] = data['DIREÇÃO (H)'].str.replace('-', '')
    data['CARTUCHOS EMPREGADOS'] = data['CARTUCHOS EMPREGADOS'].str.replace('-', '')
    data['ACERTOS'] = data['ACERTOS'].str.replace('-', '')
    data['PA'] = data['PA'].astype(str)
    data['SLANT RANGE INICIAL'] = data['SLANT RANGE INICIAL'].astype(str)
    data['SLANT RANGE FINAL'] = data['SLANT RANGE FINAL'].astype(str)
    data['TVB'] = data['TVB'].astype(str)
    data['NOTA ACERTOS'] = data['NOTA ACERTOS'].astype(str)
    data['TVB'] = data['TVB'].astype(str)

    return data


def taca_eficiencia():
    st.write('Página em desenvolvimento')
    url = os.path.normpath(os.path.abspath('TAÇA EFICIÊNCIA.xlsx'))
    sheet_name = 'DB EMPREGOS'
    todos_empregos = load_te(url, sheet_name=sheet_name)
    st.write(todos_empregos)
