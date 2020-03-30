#!/usr/bin/env python
# coding: utf-8

import datetime
import os
import pandas as pd
import unidecode

def str_to_list(value):
    return [value]

def normaliza_texto(texto):
    return unidecode.unidecode(texto)

def parse_fecha(fecha_str):
    if not fecha_str:
        return
    dia, mes, anio = fecha_str.split('/')
    return datetime.datetime(int(anio), int(mes), int(dia))

df_diarios = pd.DataFrame(columns=['fuente'])
for diario in os.listdir('descargas'):
    print(diario)
    for archivo_json in sorted(os.listdir(os.path.join('descargas', diario))):
        df_diarios = df_diarios.append(pd.read_json(os.path.join('descargas', diario, archivo_json)), ignore_index=True)
    df_diarios['fuente'][df_diarios['fuente'].isnull()] = diario

# Correcciones categoria + etiqueta
df_diarios['categoria'] = df_diarios.apply(lambda x: str_to_list(x['categoria']), axis=1)
df_diarios['etiqueta'] = df_diarios.apply(lambda x: str_to_list(x['etiqueta']), axis=1)

df_diarios['categorias_corrected'] = df_diarios['categorias']
df_diarios['etiquetas_corrected'] = df_diarios['etiquetas']
df_diarios['categorias_corrected'][df_diarios['categorias_corrected'].isnull()] = df_diarios['categoria']
df_diarios['etiquetas_corrected'][df_diarios['etiquetas_corrected'].isnull()] = df_diarios['etiqueta']

# Correcciones fecha
df_diarios['fecha_corregida'] = df_diarios['fecha']
df_diarios['fecha_corregida'] = df_diarios.apply(lambda x: parse_fecha(x['fecha_corregida']), axis=1)

# Correcciones cuerpo + titulo
df_diarios['cuerpo_corregido'] = df_diarios['cuerpo']
df_diarios['cuerpo_corregido'] = df_diarios.apply(lambda x: normaliza_texto(x['cuerpo_corregido']), axis=1)
df_diarios['titulo_corregido'] = df_diarios['titulo']
df_diarios['titulo_corregido'] = df_diarios.apply(lambda x: normaliza_texto(x['titulo_corregido']), axis=1)

