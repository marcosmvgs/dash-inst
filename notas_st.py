import os.path
import numpy as np
import pandas as pd
import streamlit as st
import altair as alt
import plotly.graph_objects as go
from PIL import Image
from sklearn.linear_model import LinearRegression
from datetime import timedelta
from NOTAS_SAGEM import main
import pyperclip
from streamlit_option_menu import option_menu
import Taca_eficiencia


st.set_page_config(layout="wide",
                   page_title='1°/3° GAV - Desempenho dos alunos',
                   page_icon=":airplane:")

def load_data_voo(caminho):
    data = pd.read_excel(caminho)
    data['DATA'] = pd.to_datetime(data['DATA'])
    return data


@st.experimental_memo
def load_ac(caminho):
    data = pd.read_excel(caminho, index_col=0)
    return data


@st.experimental_memo
def load_data_provas(caminho):
    data = pd.read_excel(caminho, sheet_name='NOTAS_GERAL')
    if data.columns[0] == 'DATA':
        data['DATA'] = pd.to_datetime(data['DATA'], format='%d%m%Y')
    return data


def get_filtro(data, parametro, filtros=None):
    lista = None
    if filtros:
        for key, value in filtros.items():
            lista = data.loc[data[key] == value][parametro].unique()
    else:
        lista = data[parametro].unique()
    return lista


def estilo_graf(grafico, titulo):
    return grafico.configure_axis(
        grid=False,
        labelFontSize=16
    ).properties(
        title={'text': titulo,
               'subtitle': '\n'},
        height=450).configure_title(
        fontSize=20,
        font='Arial',
        anchor='middle'
    ).configure_view(
        strokeWidth=0)


def resumo_ac(data, conceito, media_turma):
    total_conceitos = data[conceito].sum()
    texto = ''
    if total_conceitos > 0:
        texto_inicio = f' recebeu {total_conceitos} conceitos {conceito}, média da turma ({media_turma}), '
        j = 1
        for item, row in data[conceito].iteritems():
            if row > 0:
                if j == 1:
                    texto += f'sendo {row} em {item}, '
                elif j == (data[conceito] > 0).sum():
                    texto = texto[:-2] + texto[-2:].replace(',', '')
                    texto += f'e {row} em {item}.'
                else:
                    texto += f'{row} em {item}, '
                j += 1

    else:
        texto_inicio = f' não recebeu conceito {conceito} no curso.'
    return texto_inicio + texto.replace('Crm', 'CRM')


def calcula_media_ac(data, conceito, subprograma_selecionado):
    subprograma_selecionado = subprograma_selecionado
    data2 = data.query(f"SUBPROGRAMA == @subprograma_selecionado")
    media_ac_turma = round(data2[conceito].sum() / len(data2['ALUNO'].unique()), 2)
    return media_ac_turma


def copiar_resumo(conteudo):
    return pyperclip.copy(conteudo)


def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.markdown("<h1 style='text-align: center; color: black;'>1°/3° GAV headline</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; color: black;'>Quadro de acompanhamento do desempenho dos alunos</h3>", unsafe_allow_html=True)
        coluna1, coluna2, coluna3 = st.columns((4.65, 2, 3.35))
        with coluna1:
            pass
        with coluna2:
            image = Image.open(os.path.normpath(os.path.abspath('1-3gav.png')))
            st.image(image, width=100)
            with coluna3:
                pass
        st.text_input(
            "Digite a senha", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True

if check_password():
  selected = option_menu(
    menu_title=None,
    options=['Quadro Geral', 'Taça Eficiência'],
    default_index=0,
    orientation='horizontal',
    icons=['arrow-up-right-square-fill', 'bullseye'],
    styles={
        "container": {"padding": "0!important",
                      "background-color": "#e3e3e3",
                      "width": "450px"},
        "icon": {"color": "black", "font-size": "25px"},
        "nav-link": {"font-size": "17px", "text-align": "center", "margin": "0px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "#c8c8c8",
                              "color": "black",
                              "font-weight": "normal"},})


  image = Image.open(os.path.normpath(os.path.abspath('1-3gav.png')))
  st.sidebar.image(image, width=70)
  st.sidebar.markdown('### Piloto')

  # Carregando os dados
  url2 = os.path.normpath(os.path.abspath('TODAS_FICHAS.xlsx'))
  todas_fichas = load_data_voo(url2)
  fichas_totais = {'SPFO-1': 45,
                   'SPFO-2': 43,
                   'SPFO-3': 20}
  todas_fichas['INSTRUTOR'] = todas_fichas['INSTRUTOR'].str.capitalize()

  url_ac = os.path.normpath(os.path.abspath('AC.xlsx'))
  todos_ac = load_ac(url_ac)
  todos_ac['ITEM'] = todos_ac['ITEM'].str.capitalize()

  ulr_provas = os.path.normpath(os.path.abspath('PROVAS 2022.xlsx'))
  todas_provas = load_data_provas(ulr_provas)

  # Filtros
  lista_alunos = todas_fichas['ALUNO'].unique()
  aluno_selecionado = st.sidebar.selectbox('Selecione o Aluno', options=lista_alunos)

  lista_subprogramas = todas_fichas.loc[todas_fichas['ALUNO'] == aluno_selecionado, 'SUBPROGRAMA'].unique()
  subprograma_selecionado = st.sidebar.selectbox('Selecione o Subprograma', options=lista_subprogramas)

  options = st.sidebar.multiselect(
      label='Tipo de Missão',
      options=['Normal', 'Extra', 'Revisão'],
      default='Normal')

  tipo_selecionado = ''
  for tipo in options:
      tipo_selecionado += tipo + ' '

  st.sidebar.markdown(f'Você selecionou: {tipo_selecionado}')


  fichas_selecionadas = todas_fichas.query("ALUNO == @aluno_selecionado & SUBPROGRAMA ==  @subprograma_selecionado & TIPO == @options").set_index('DATA')
  ac_selecionado = todos_ac.query("ALUNO == @aluno_selecionado & SUBPROGRAMA == @subprograma_selecionado")
  provas_selecionadas = todas_provas.query("ALUNO == @aluno_selecionado & SUBPROGRAMA == @subprograma_selecionado")

  ### KPIS ###

  # KPI 1 - Média de voo do aluno
  kpi1_med_voo_al = round(fichas_selecionadas['GRAU'].mean(), 2)
  kpi1_media_anterior = fichas_selecionadas.head(fichas_selecionadas.shape[0] - 5)['GRAU'].mean()

  kpi1_delta = f'{round((kpi1_med_voo_al - kpi1_media_anterior) * 100 / kpi1_media_anterior, 2)}' \
                    f'%'.replace('.', ',')


  # KPI 2 - Média de voo da turma
  kpi2_med_voo_turma = round(todas_fichas['GRAU'].mean(), 2)
  todas_fichas_index_data = todas_fichas.set_index('DATA')
  media_turma_anterior = round(todas_fichas_index_data.head(todas_fichas_index_data.shape[0] - 10)['GRAU'].mean(), 2)

  delta_media_turma_voo = f'{round((kpi2_med_voo_turma - media_turma_anterior) * 100 / media_turma_anterior, 2)}' \
                          f'%'.replace('.', ',')


  # KPI 3 - Porcentagem de fichas realizadas
  kpi3_fichas_realizadas = str(round((fichas_selecionadas.shape[0] * 100
                                      / fichas_totais.get(subprograma_selecionado)), 2)) + '%'

  # KPI 4 - Classificação de voo
  df_medias_alunos_voo = todas_fichas.loc[todas_fichas['SUBPROGRAMA'] == subprograma_selecionado].groupby('ALUNO').mean('GRAU')
  df_medias_alunos_voo['RANKING'] = df_medias_alunos_voo['GRAU'].rank(ascending=False)
  df_medias_alunos_voo['RANKING'] = df_medias_alunos_voo['RANKING'].apply(lambda x: str(int(x)) + f'º/'
                                                                                                  f'{df_medias_alunos_voo.shape[0]}')
  kpi4_class_voo = df_medias_alunos_voo.loc[aluno_selecionado]['RANKING']

  # KPI 5 - Média de Prova Aluno
  kpi5_media_al_prova = round(provas_selecionadas['NOTA'].mean(), 2)

  # KPI 6 - Média de Prova Turma
  kpi6_media_turma_prova = round(todas_provas['NOTA'].mean(), 2)

  # KPI 7 - Quantidade de provas realizadas aluno
  kpi7_qtd_provas = round(provas_selecionadas.shape[0])

  df_medias_alunos_provas = todas_provas.loc[todas_provas['SUBPROGRAMA'] == subprograma_selecionado].groupby(
      'ALUNO').mean('NOTA')
  df_medias_alunos_provas['RANKING'] = df_medias_alunos_provas['NOTA'].rank(ascending=False)
  df_medias_alunos_provas['RANKING'] = df_medias_alunos_provas['RANKING'].apply(
      lambda x: str(int(x)) + f'º/{df_medias_alunos_provas.shape[0]}')

  # KPI 8 - Classificação de provas Aluno
  kpi8_class_prova = df_medias_alunos_provas.loc[aluno_selecionado]['RANKING']

  #### RESUMO HOPE #####

  # TEXTO PARTE DE VOO E CLASSIFICAÇÕES
  parte1 = f'Concluiu o {subprograma_selecionado}  média {kpi1_med_voo_al} ' \
           f'(média da turma {kpi2_med_voo_turma}), classificando-se em {kpi4_class_voo}. '

  # TEXTO DEFICIENTES
  graus_deficiente = fichas_selecionadas.loc[fichas_selecionadas['GRAU'] == 2].reset_index()
  qtde_deficiente = graus_deficiente.shape[0]
  qtde_deficiente_fase = graus_deficiente.value_counts('FASE')

  texto_completo_deficiente = ''
  primeiro_deficiente = ''
  resumo_deficientes = ''
  if qtde_deficiente > 0:
      deficiente = f'Recebeu {qtde_deficiente} grau(s) DEFICIENTE no curso. '
      j = 0
      texto_demais_deficientes = ''
      for i in qtde_deficiente_fase.index:
          qtd_def_fase = qtde_deficiente_fase.loc[i]
          if j == 0:
               primeiro_deficiente = f'Sendo {qtd_def_fase} em {i}. '
          else:
              primeiro_deficiente = primeiro_deficiente.replace('.', ',')
              demais_deficientes = f'{qtd_def_fase} em {i}, '
              if j == qtde_deficiente - 1:
                  demais_deficientes = demais_deficientes.replace(',', '.')
              texto_demais_deficientes += demais_deficientes
          j +=1
          resumo_deficientes = primeiro_deficiente + texto_demais_deficientes
      texto_completo_deficiente = deficiente + resumo_deficientes
  else:
      texto_completo_deficiente = 'Não recebeu grau DEFICIENTE no curso.'

  # TEXTO AFETIVO-COGNITIVO
  media_conceito_deficiente_turma = calcula_media_ac(todos_ac, 'DEFICIENTE', subprograma_selecionado)
  media_conceito_pm_turma = calcula_media_ac(todos_ac, 'PRECISA MELHORAR', subprograma_selecionado)
  media_conceito_destac_turma = calcula_media_ac(todos_ac, 'DESTACOU-SE', subprograma_selecionado)
  texto_afet_cogn = f'No campo Afetivo-Cognitivo, '
  df_ac_item = ac_selecionado.groupby('ITEM').sum(['PRECISA MELHORAR', 'DEFICIENTE', 'DESTACOU-SE'])

  # TEXTO INTELECTUAL
  texto_intelectual = f'No campo intelectual obteve média {kpi5_media_al_prova} (média da turma {kpi6_media_turma_prova}), ' \
                      f'classificando-se em {kpi4_class_voo}.'

  # TABELA DE FICHAS
  df = fichas_selecionadas.reset_index()
  df['DATA'] = df['DATA'].dt.strftime('%d-%m-%Y')
  fig = go.Figure(data=[go.Table(
      columnorder=[0, 1, 2, 3, 4, 5, 6, 7],
      header=dict(values=list(['DATA', 'INSTRUTOR', 'ALUNO', 'SUBPROGRAMA', 'CODIGO', 'FASE', 'GRAU']),
                  fill_color='#c8c8c8',
                  align='center',
                  font=dict(color='black', size=20),
                  height=40),
      cells=dict(values=[df.DATA, df.INSTRUTOR, df.ALUNO, df.SUBPROGRAMA, df['CODIGO'], df.FASE, df.GRAU],
                 fill_color='#f6f6f6 ',
                 align='center',
                 height=30,
                 font=dict(color='black', size=17)))
  ])

  # GRÁFICOS

  # Notas por mês
  df_media_mes = todas_fichas.groupby([pd.Grouper(key='DATA', freq='M'), "ALUNO"]).mean('GRAU').reset_index()
  df_media_mes['GRAU'] = df_media_mes['GRAU'].apply(lambda x: round(x, 2))
  df_media_mes_aluno = df_media_mes.loc[df_media_mes['ALUNO'] == aluno_selecionado]

  g_media_aluno = alt.Chart(df_media_mes_aluno)
  g_media_turma = alt.Chart(todas_fichas.loc[todas_fichas['SUBPROGRAMA'] == subprograma_selecionado])
  linha_media_aluno = g_media_aluno.mark_line(point=True,
                                              size=5,
                                              color='#063970',
                                              strokeCap='round',
                                              opacity=0.9).encode(
      x=alt.X('DATA:N', timeUnit='month', title=''),
      y=alt.Y('average(GRAU)', scale=alt.Scale(domain=[3, 6.5]), axis=alt.Axis(ticks=False,
                                                                               labels=False,
                                                                               domain=False,
                                                                               labelPadding=10), title=''))

  linha_media_turma = g_media_turma.mark_area(point=False,
                                              size=3,
                                              color='#abdbe3',
                                              opacity=0.5).encode(
      y=alt.Y('average(GRAU)', scale=alt.Scale(domain=[3, 6])),
      x=alt.X('DATA:T', timeUnit='month')
      )

  labels = g_media_aluno.mark_text(
      align='left', dx=5, dy=25, fontSize=15, fontWeight='bold'
  ).encode(
      x=alt.X('DATA:T', timeUnit='month'),
      y=alt.Y('average(GRAU)', scale=alt.Scale(domain=[3, 6])),
      text='average(GRAU)'
  )

  df_regressao = df_media_mes_aluno.copy()

  df_regressao = df_regressao.set_index('DATA')
  df_regressao['ORDINAL'] = df_regressao.index.map(pd.Timestamp.toordinal)

  model = LinearRegression()

  x = df_regressao[['ORDINAL']]
  y = df_regressao[['GRAU']]

  model.fit(x, y)

  x1 = df_regressao.ORDINAL.min()
  x2 = df_regressao.ORDINAL.max()

  if df_regressao.index.month[0] == 1:
      x1_date = df_regressao[df_regressao.ORDINAL.eq(x1)].index[0]
  else:
      x1_date = df_regressao[df_regressao.ORDINAL.eq(x1)].index[0] - timedelta(days=30)

  if df_regressao.index.month[-1] == 11:
      x2_date = df_regressao[df_regressao.ORDINAL.eq(x2)].index[0] + timedelta(days=30)
  elif df_regressao.index.month[-1] == 12:
      x2_date = df_regressao[df_regressao.ORDINAL.eq(x2)].index[0]
  else:
      x2_date = df_regressao[df_regressao.ORDINAL.eq(x2)].index[0] + timedelta(days=60)

  x1 = x1_date.toordinal()
  x2 = x2_date.toordinal()

  y1 = round(model.predict(np.array([[x1]]))[0][0], 2)
  y2 = round(model.predict(np.array([[x2]]))[0][0], 2)

  df_predict = pd.DataFrame({'DATA_': [x1_date, x2_date],
                             'GRAU_': [y1, y2]})

  linha_regressao = alt.Chart(df_predict).mark_line(point=False,
                                                    size=10,
                                                    color='#000000',
                                                    opacity=0.1).encode(
          y=alt.Y('GRAU_', scale=alt.Scale(domain=[3, 6])),
          x=alt.X('DATA_', timeUnit='month')
          )

  labels_regressao = alt.Chart(df_predict).mark_text(
      align='left',
      dx=5,
      dy=25,
      fontSize=15,
      fontWeight='bold',
      color='gray'
  ).encode(
      x=alt.X('DATA_', timeUnit='month'),
      y=alt.Y('GRAU_', scale=alt.Scale(domain=[3, 6])),
      text='GRAU_'
  )

  # Notas por FASE
  df_nota_fase = fichas_selecionadas.groupby('FASE').mean('GRAU').round(2).reset_index()
  grf_nota_fase = alt.Chart(df_nota_fase)

  df_media_turma_fase = todas_fichas.query("SUBPROGRAMA ==  @subprograma_selecionado").groupby('FASE').mean('GRAU').round(2).reset_index()
  grf_media_turma_fase = alt.Chart(df_media_turma_fase)

  barras_nota_fase = grf_nota_fase.mark_bar(
      size=20,
      color='#303030',
      cornerRadiusBottomRight=3,
      cornerRadiusTopRight=3).encode(
      x=alt.X('GRAU', title=''),
      y=alt.Y('FASE', title='')
  )


  area_media_turma_fase = grf_media_turma_fase.mark_area(point=False,
                                                         size=3,
                                                         color='#abdbe3',
                                                         opacity=0.5).encode(
      x=alt.X('GRAU:Q', title='', axis=alt.Axis(ticks=False,
                                              labels=False,
                                              domain=False)),
      y=alt.Y('FASE', title='', axis=alt.Axis(ticks=False,
                                              labels=True,
                                              domain=False,
                                              labelPadding=10)))

  texto_media_fase = grf_nota_fase.mark_text(align='right',
                                             baseline='middle',
                                             color='#ffffff',
                                             dx=-10
                                             ).encode(text='GRAU:Q', x='GRAU:Q', y='FASE')

  # Nota por INSTRUTOR
  df_nota_in = fichas_selecionadas.groupby('INSTRUTOR').mean('GRAU').round(2).reset_index()
  grf_nota_in = alt.Chart(df_nota_in)

  df_media_turma_in = todas_fichas.query("SUBPROGRAMA ==  @subprograma_selecionado").groupby('INSTRUTOR').mean('GRAU').round(2).reset_index()
  grf_media_turma_in = alt.Chart(df_media_turma_in)

  barras_nota_in = grf_nota_in.mark_bar(
      size=20,
      color='#303030',
      cornerRadiusBottomRight=3,
      cornerRadiusTopRight=3).encode(
      x=alt.X('GRAU', title=''),
      y=alt.Y('INSTRUTOR', sort="-x")
  )

  area_media_turma_in = grf_media_turma_in.mark_area(
      point=False,
      size=3,
      color='#abdbe3',
      opacity=0.5).encode(
      x=alt.X('GRAU', title='', axis=alt.Axis(ticks=False,
                                              labels=False,
                                              domain=False)),
      y=alt.Y('INSTRUTOR', title='', axis=alt.Axis(ticks=False,
                                              labels=True,
                                              domain=False,
                                              labelPadding=10),
             sort='-x'))

  texto_media_instrutor = barras_nota_in.mark_text(align='right',
                                             baseline='middle',
                                             color='#ffffff',
                                             dx=-10
                                             ).encode(text='GRAU:Q', x='GRAU:Q', y='INSTRUTOR')


  # Gráfico AC

  soma_dt = ac_selecionado['DESTACOU-SE'].sum()
  soma_df = ac_selecionado['DEFICIENTE'].sum()
  soma_pm = ac_selecionado['PRECISA MELHORAR'].sum()

  dados_ac = pd.DataFrame({'CONCEITOS': ['DESTACOU-SE', 'DEFICIENTE', 'PRECISA MELHORAR'],
                            'soma': [soma_dt, soma_df, soma_pm]})

  base_ac = alt.Chart(dados_ac).encode(
      theta=alt.Theta("soma:Q", stack=True),
      radius=alt.Radius("soma:Q", scale=alt.Scale(type="sqrt", zero=True, rangeMin=20)),
      color=alt.Color("CONCEITOS:N",
                      scale=alt.Scale(domain=['PRECISA MELHORAR', 'DEFICIENTE', 'DESTACOU-SE'],
                                      range=['orange', '#cc0000', '#063970']),
                      legend=alt.Legend(orient='top', title='', labelFontSize=15, symbolSize=300, columnPadding=120, padding=20)))

  c1 = base_ac.mark_arc(innerRadius=20, stroke="#ffffff")
  c2 = base_ac.mark_text(radiusOffset=20, fontSize=20).encode(text="soma:Q")

  # Gráfico AC por item
  ordem = ['DESTACOU-SE', 'PRECISA MELHORAR', 'DEFICIENTE']
  base_grafico = alt.Chart(ac_selecionado).transform_fold(
      ['DEFICIENTE', 'PRECISA MELHORAR', 'DESTACOU-SE'],
      as_=['column', 'somatorio']
  )
  grafico_stacked = base_grafico.mark_bar(size=20,
                                          color='#063970',
                                          cornerRadiusBottomRight=3,
                                          cornerRadiusTopRight=3).encode(
      y=alt.Y('ITEM:N', title='', axis=alt.Axis(labelLimit=2000,
                                                domain=False,
                                                ticks=False,
                                                labelPadding=11.5), sort='-x'),
      x=alt.X('somatorio:Q', title='',
              axis=alt.Axis(domain=False,
                            ticks=False,
                            labels=False)),
      color=alt.Color('column:N',
                      sort = alt.EncodingSortField('somatorio:Q'),
                      scale=alt.Scale(domain=['PRECISA MELHORAR', 'DEFICIENTE', 'DESTACOU-SE'],
                                      range=['orange', '#cc0000', '#063970']),
                      legend=None
                      ),
      order=alt.Order('color_site_sort_index:Q'))

  texto_stacked = base_grafico.mark_text(dx=-9, dy=1, color='white').encode(
      x=alt.X('somatorio:Q', stack='zero'),
      y=alt.Y('ITEM:N'),
      detail='column:N',
      text=alt.Text('somatorio:Q', format='.0f')
  )


  # GRÁFICO NOTA POR PROVA
  base_notas = alt.Chart(provas_selecionadas)
  grf_notas_prova = base_notas.mark_bar(
      size=20,
      color='#303030',
      cornerRadiusBottomRight=3,
      cornerRadiusTopRight=3).encode(
      x='NOTA:Q',
      y='PROVA:N')

  df_media_turma_prova = todas_provas.query("SUBPROGRAMA ==  @subprograma_selecionado").groupby('PROVA').mean('NOTA').round(2).reset_index()
  grf_notas_prova_turma = alt.Chart(df_media_turma_prova).mark_area(
      point=False,
      size=3,
      color='#abdbe3',
      opacity=0.5).encode(
      x=alt.X('NOTA', title='', axis=alt.Axis(ticks=False,
                                              labels=False,
                                              domain=False)),
      y=alt.Y('PROVA', title='', axis=alt.Axis(ticks=False,
                                              labels=True,
                                              domain=False,
                                              labelPadding=10)))

  texto_nota_prova = base_notas.mark_text(align='right',
                                                     baseline='middle',
                                                     color='#ffffff',
                                                     dx=-10).encode(
      text='NOTA:Q', x='NOTA:Q', y='PROVA:N')

  st.sidebar.write(f"Último voo na base de dados: {fichas_selecionadas.iloc[-1:].index.strftime('%d-%m-%Y')[0]}")

  if selected == 'Quadro Geral':
      ###### EXIBIÇÃO TÍTULO ######
      container_titulo = st.container()
      with container_titulo:
          col_t1, col_t2, col_t3 = st.columns([2.5, 6, 1.5])
          with col_t1:
              pass
          with col_t2:
              st.markdown("## :bar_chart:    Quadro de acompanhamento de Pilotos    :airplane:")
              st.markdown('##')
              st.markdown('##')
          with col_t3:
              pass

      ################### EXIBIÇÃO KPI'S ######################
      container_kpi_voo = st.container()
      with container_kpi_voo:
          kpi1_voo, kpi2_voo, kpi3_voo, kpi4_voo = st.columns(4)
          with kpi1_voo:
              st.metric('Média voo', value=round(kpi1_med_voo_al, 2), delta=kpi1_delta)
          with kpi2_voo:
              st.metric('Média voo turma', value=round(kpi2_med_voo_turma, 2))
          with kpi3_voo:
              st.metric('Qtd Fichas', value=kpi3_fichas_realizadas)
          with kpi4_voo:
              st.metric('Class. Voo', value=kpi4_class_voo)

      container_kpi_provas = st.container()
      with container_kpi_provas:
          kpi1_provas, kpi2_provas, kpi3_provas, kpi4_provas = st.columns(4)
          with kpi1_provas:
              st.metric('Média provas', value=kpi5_media_al_prova)
          with kpi2_provas:
              st.metric('Média provas turma', value=kpi6_media_turma_prova)
          with kpi3_provas:
              st.metric('Qtd Provas', value=kpi7_qtd_provas)
          with kpi4_provas:
              st.metric('Class. Prova', value=kpi8_class_prova)

      #### EXIBIÇÃO RESUMO #####
      expander1 = st.expander('Ver resumo do desempenho do aluno')
      with expander1:
          st.markdown(parte1 + texto_completo_deficiente)
          afetivo_cognitivo = texto_afet_cogn + \
                              resumo_ac(df_ac_item, 'DEFICIENTE', media_conceito_deficiente_turma) + \
                              resumo_ac(df_ac_item, 'PRECISA MELHORAR', media_conceito_pm_turma) + \
                              resumo_ac(df_ac_item, 'DESTACOU-SE', media_conceito_destac_turma)
          st.write(afetivo_cognitivo)
          st.write(texto_intelectual)
          arguments = parte1 + texto_completo_deficiente + "\n" + afetivo_cognitivo + "\n" + texto_intelectual
          st.button(label="Copiar conteúdo", on_click=copiar_resumo, args=arguments)

      expander2 = st.expander('Ver tabela de fichas')
      with expander2:
          st.plotly_chart(fig, use_container_width=True)


      ### EXIBIÇÃO GRÁFICOS ####
      container_graficos1 = st.container()
      with container_graficos1:
          grafico_grau_mes = estilo_graf((linha_media_turma + linha_regressao + labels_regressao + linha_media_aluno + labels), 'Graus por mês').configure_point(
              size=150,
              color='#000000')
          st.altair_chart(grafico_grau_mes, use_container_width=True)

          col1, col2 = st.columns(2)
          col3, col4, col5, col6 = st.columns([0.5, 49.5, 1, 49])
          with col1:
              st.altair_chart(estilo_graf((area_media_turma_in + barras_nota_in + texto_media_instrutor), 'Grau por Instrutor'),
                              use_container_width=True)
          with col2:
              st.altair_chart(estilo_graf((area_media_turma_fase + barras_nota_fase + texto_media_fase), 'Grau por fase'),
                              use_container_width=True)
          with col3:
              pass
          with col4:

              st.altair_chart((c1 + c2).properties(title={'text': 'Somatório de Conceitos',
                                                          'subtitle': '\n',
                                                          'subtitleFontSize': 10}).configure_title(
                  fontSize=20,
                  font='Arial',
                  anchor='middle').properties(height=400),
                      use_container_width=True)
          with col5:
              pass
          with col6:
              st.altair_chart(estilo_graf((grafico_stacked + texto_stacked), 'Somatório de conceitos por Item'), use_container_width=True)

          col7, col8 = st.columns(2)
          with col7:
              st.altair_chart(estilo_graf((grf_notas_prova_turma + grf_notas_prova + texto_nota_prova), 'Nota por prova'), use_container_width=True)
          with col8:
              pass

  if selected == 'Taça Eficiência':
      Taca_eficiencia.taca_eficiencia()

