# -*- coding: utf-8 -*-
"""
Created on Fri Oct 18 17:32:46 2024

@author: Sammy
"""

# Importamos bibliotecas
import pandas as pd
import duckdb
import numpy as np 
import seaborn as sns
import matplotlib.pyplot as plt
import os

#%%===========================================================================
# Importamos los datasets
#=============================================================================

carpeta = r'C:\Users\Nt\Desktop\Carrera\Laboratorio de Datos\An-lisis-liga-espa-ola'

equipo = pd.read_csv(carpeta+'equipo_esp.csv')
plantel = pd.read_csv(carpeta+'plantel_esp.csv')
partido = pd.read_csv(carpeta+'partido_esp.csv')
jugador = pd.read_csv(carpeta+"jugador.csv")
atributos = pd.read_csv(carpeta+"atributos.csv", parse_dates=["Fecha"])

# Carpeta donde se guardan las imágenes
os.makedirs(carpeta+'imagenes', exist_ok=True)
img = carpeta + 'imagenes\\'

#%% Determinamos un criterio de selección de temporadas

equipos_x_temporada = partido.groupby('Temporada')['Id_Local'].nunique()
igual_num_equipos = equipos_x_temporada.nunique() == 1

if igual_num_equipos:
    print("Cada temporada tiene igual número de equipos.")
else:
    print(equipos_x_temporada) 

#%%
num_partidos_temp = partido['Temporada'].value_counts().sort_index()

temporadas_0 = num_partidos_temp.loc['2008/2009':'2011/2012']
temporadas_1 = num_partidos_temp.loc['2009/2010':'2012/2013']
temporadas_2 = num_partidos_temp.loc['2010/2011':'2013/2014']
temporadas_3 = num_partidos_temp.loc['2011/2012':'2014/2015']
temporadas_4 = num_partidos_temp.loc['2012/2013':'2015/2016']

diferencias = (temporadas_0.diff(), temporadas_1.diff(), temporadas_2.diff(),
               temporadas_3.diff(), temporadas_4.diff())

for i in diferencias:
    menos_20 = abs(i) < 20
    print(menos_20) 

#%% Creamos las tablas con las temporadas de interés

partido_ok  = partido[(partido['Temporada'] >= '2011/2012') & (partido['Temporada'] <= '2014/2015')]
plantel_ok  = plantel[(plantel['Temporada'] >= '2011/2012') & (plantel['Temporada'] <= '2014/2015')]

equipo_0  = duckdb.sql('''SELECT * FROM equipo INNER JOIN partido_ok ON Id_Equipo = Id_Local OR Id_Equipo = Id_Visitante''').df()
equipo_ok = equipo_0[['Id_Equipo', 'Nombre', 'Temporada']].drop_duplicates()

#%%===========================================================================
# CONSULTAS SQL
#=============================================================================

#%% Equipo más ganador en general 
consulta_victorias = '''SELECT Id_Local AS Id_Equipo FROM partido_ok WHERE Gol_local > Gol_visitante
                        UNION ALL
                        SELECT Id_Visitante AS Id_Equipo FROM partido_ok WHERE Gol_visitante > Gol_local'''
equipo_ganador_0 = duckdb.sql(consulta_victorias).df()                    

consulta_ganador = '''SELECT Id_Equipo, COUNT(*) AS Victorias FROM equipo_ganador_0
                      GROUP BY Id_Equipo ORDER BY Victorias DESC LIMIT 1'''  
equipo_ganador_1 = duckdb.sql(consulta_ganador).df()

consulta_nombre = '''SELECT DISTINCT Nombre FROM equipo_ok AS e
                     INNER JOIN equipo_ganador_1 AS p ON e.Id_Equipo = p.Id_equipo'''
equipo_ganador = duckdb.sql(consulta_nombre).df()

#%% Equipo más perdedor por AÑO
partido_ok_por_año = partido[(partido['Temporada'] >= '2010/2011') & (partido['Temporada'] <= '2015/2016')]

equipo_0_por_año  = duckdb.sql('''SELECT * FROM equipo INNER JOIN partido_ok_por_año ON Id_Equipo = Id_Local OR Id_Equipo = Id_Visitante''').df()
equipo_ok_por_año = equipo_0_por_año[['Id_Equipo', 'Nombre', 'Temporada']].drop_duplicates()

consulta_derrotas = '''SELECT Id_Local AS Id_Equipo, Fecha FROM partido_ok_por_año WHERE Gol_local < Gol_visitante
                       UNION ALL
                       SELECT Id_Visitante AS Id_Equipo, Fecha FROM partido_ok_por_año WHERE Gol_visitante < Gol_local'''
equipo_perdedor_0 = duckdb.sql(consulta_derrotas).df() 

consulta_año = '''SELECT *, EXTRACT(YEAR FROM CAST(Fecha AS DATE)) AS Año FROM equipo_perdedor_0'''
equipo_perdedor_año = duckdb.sql(consulta_año).df()

consulta_perdedor = '''SELECT Id_Equipo, Año, COUNT(*) AS Derrotas FROM equipo_perdedor_año
                       GROUP BY Id_Equipo, Año ORDER BY Año, Derrotas DESC'''  
equipo_perdedor_1 = duckdb.sql(consulta_perdedor).df()

consulta_max_perdedor = '''SELECT Año, Id_Equipo, Derrotas FROM equipo_perdedor_1 AS ep
                           WHERE Derrotas = (SELECT MAX(Derrotas) FROM equipo_perdedor_1 WHERE Año = ep.Año)
                           ORDER BY Año'''
equipo_max_perdedor = duckdb.sql(consulta_max_perdedor).df()

consulta_nombre_perdedor = '''SELECT DISTINCT Nombre, p.Año FROM equipo_ok_por_año AS e
                              INNER JOIN equipo_max_perdedor AS p ON e.Id_Equipo = p.Id_equipo
                              ORDER BY Año ASC'''
equipo_perdedor = duckdb.sql(consulta_nombre_perdedor).df()

#%% Equipo con más empates del último año 
partido_por_año    = partido[(partido['Temporada'] >= '2010/2011') & (partido['Temporada'] <= '2015/2016')]
consulta_por_año   = '''SELECT *, EXTRACT(YEAR FROM CAST(Fecha AS DATE)) AS Año FROM partido_por_año'''
partido_ok_por_año = duckdb.sql(consulta_por_año).df()

consulta_empate = '''SELECT Id_Local AS Id_Equipo, Año FROM partido_ok_por_año WHERE Resultado = 'Empate'
                     UNION ALL 
                     SELECT Id_Visitante AS Id_Equipo, Año FROM partido_ok_por_año
                     WHERE Resultado = 'Empate' AND Año = 2015'''
equipos_empate = duckdb.sql(consulta_empate).df()

consulta_empate_ok = '''SELECT Id_Equipo, COUNT(*) AS Empates FROM equipos_empate
                        GROUP BY Id_Equipo ORDER BY Empates DESC LIMIT 1'''  
equipo_empate = duckdb.sql(consulta_empate_ok).df()

consulta_nombre  = '''SELECT DISTINCT Nombre FROM equipo_ok_por_año AS e
                      INNER JOIN equipo_empate AS p ON e.Id_Equipo = p.Id_equipo'''
equipo_empate_2015 = duckdb.sql(consulta_nombre).df()

#%% Equipo con más goles a favor 
consulta_gol_favor = '''SELECT Id_Local AS Id_Equipo, Gol_local AS Goles_a_favor FROM partido_ok
                        UNION ALL
                        SELECT Id_Visitante AS Id_Equipo, Gol_visitante AS Goles_a_favor FROM partido_ok'''
equipo_goles_por_fecha = duckdb.sql(consulta_gol_favor).df()

consulta_goles = '''SELECT Id_Equipo, SUM(Goles_a_favor) AS Goles_a_favor FROM equipo_goles_por_fecha
                    GROUP BY Id_Equipo ORDER BY Goles_a_favor DESC LIMIT 1'''
equipo_max_goles_favor = duckdb.sql(consulta_goles).df()

consulta_nombre = '''SELECT DISTINCT Nombre FROM equipo_ok AS e
                     INNER JOIN equipo_max_goles_favor AS p ON e.Id_Equipo = p.Id_Equipo'''
equipo_goles_a_favor = duckdb.sql(consulta_nombre).df()

#%% Equipo con mayor diferencia de goles 
consulta_gol_diff = '''SELECT Id_Local AS Id_Equipo, (Gol_local-Gol_visitante) AS Goles_a_favor FROM partido_ok
                       UNION ALL
                       SELECT Id_Visitante AS Id_Equipo, (Gol_visitante-Gol_local) AS Goles_a_favor FROM partido_ok'''
equipo_gol_diff_por_fecha = duckdb.sql(consulta_gol_diff).df()

consulta_gol_diff_ok = '''SELECT Id_Equipo, SUM(Goles_a_favor) AS Gol_diferencia FROM equipo_gol_diff_por_fecha
                          GROUP BY Id_Equipo ORDER BY Gol_diferencia DESC LIMIT 1'''  
equipo_max_gol_diff = duckdb.sql(consulta_gol_diff_ok).df()

consulta_nombre = '''SELECT DISTINCT Nombre FROM equipo_ok AS e
                     INNER JOIN equipo_max_gol_diff AS p ON e.Id_Equipo = p.Id_equipo'''
equipo_gol_diff = duckdb.sql(consulta_nombre).df()

#%% Número de jugadores de cada equipo 
consulta_num_jugadores = '''SELECT Id_Equipo, COUNT(Id_Jugador) AS Número_jugadores
                            FROM plantel_ok GROUP BY Id_Equipo'''
num_jugadores = duckdb.sql(consulta_num_jugadores).df()

consulta_nombre = '''SELECT DISTINCT Nombre, Número_jugadores FROM equipo_ok AS e
                     INNER JOIN num_jugadores AS p ON e.Id_Equipo = p.Id_equipo
                     ORDER BY Número_jugadores DESC'''
num_jugadores_por_equipo = duckdb.sql(consulta_nombre).df()

#%% Jugadores que más partidos ganó su equipo
consulta_jugadores_mas_ganadores = '''SELECT DISTINCT Id_Jugador FROM plantel_ok WHERE Id_Equipo = 8634'''
jugadores_mas_ganadores_0 = duckdb.sql(consulta_jugadores_mas_ganadores).df()

consulta_nombre = '''SELECT DISTINCT Nombre FROM jugador AS e
                     INNER JOIN jugadores_mas_ganadores_0 AS p ON e.Id_Jugador = p.Id_Jugador'''
jugadores_mas_ganadores     = duckdb.sql(consulta_nombre).df()
lista_jugadores_mas_ganadores = np.array(jugadores_mas_ganadores['Nombre']).tolist()

#%% Jugador que estuvo en más equipos
consulta_mas_equipos = '''SELECT Id_Jugador, COUNT(DISTINCT Id_Equipo) AS num_equipos
                          FROM plantel_ok GROUP BY Id_Jugador ORDER BY num_equipos DESC LIMIT 1'''
jugador_mas_equipos_0 = duckdb.sql(consulta_mas_equipos).df()

consulta_nombre = '''SELECT DISTINCT Nombre FROM jugador AS e
                     INNER JOIN jugador_mas_equipos_0 AS p ON e.Id_Jugador = p.Id_Jugador'''
jugador_mas_equipos = duckdb.sql(consulta_nombre).df()

#%% Jugador con menor variación de potencia
jugadores_todas_temporadas = duckdb.query("""
    SELECT Id_Jugador FROM plantel_ok
    WHERE Temporada IN ('2011/2012', '2012/2013', '2013/2014', '2014/2015')
    GROUP BY Id_Jugador HAVING COUNT(DISTINCT Temporada) = 3;             
""")

potencial_ok = duckdb.query("""
    SELECT T1.Id_Jugador, Potencial, Fecha
    FROM jugadores_todas_temporadas as T1 LEFT JOIN atributos as T2
    ON T1.Id_Jugador = T2.Id_Jugador
""")

res_raw = duckdb.query("""
    SELECT Id_Jugador, STDDEV(Potencial) AS Variacion_Potencial 
    FROM potencial_ok GROUP BY Id_Jugador ORDER BY Variacion_Potencial DESC;
""").df()

Jugador_Variacion_Potencial = duckdb.query("SELECT * FROM res_raw WHERE Variacion_Potencial IS NOT NULL").df()

Jugador_Mayor_Variacion = duckdb.query("""
    SELECT * FROM Jugador_Variacion_Potencial
    WHERE Variacion_Potencial = (SELECT MAX(Variacion_Potencial) FROM Jugador_Variacion_Potencial)
""")
Jugador_Menor_Variacion = duckdb.query("""
    SELECT * FROM Jugador_Variacion_Potencial
    WHERE Variacion_Potencial = (SELECT MIN(Variacion_Potencial) FROM Jugador_Variacion_Potencial)
""")
Nombre_Menor_Variacion = duckdb.query("""
    SELECT Nombre FROM Jugador_Menor_Variacion as T1 INNER JOIN jugador as T2 on T1.Id_Jugador = T2.Id_Jugador
""")

#%%===========================================================================
# Visualizaciones
#=============================================================================

plt.rcParams["figure.figsize"] = (8, 6)
plt.rcParams['font.size']        = 12            
plt.rcParams['font.family']      = 'Verdana' 
plt.rcParams['axes.labelsize']   = 14       
plt.rcParams['axes.titlesize']   = 16      
plt.rcParams['legend.fontsize']  = 14    
plt.rcParams['xtick.labelsize']  = 12      
plt.rcParams['ytick.labelsize']  = 12 

#%% Goles a favor y en contra
consulta_f_c = '''SELECT Id_Equipo, SUM(Gol_favor) AS Gol_favor, SUM(Gol_contra) AS Gol_contra
                  FROM (
                      SELECT Id_Local AS Id_Equipo, SUM(Gol_local) AS Gol_favor, SUM(Gol_visitante) AS Gol_contra
                      FROM partido_ok GROUP BY Id_Local
                      UNION ALL
                      SELECT Id_visitante AS Id_Equipo, SUM(Gol_visitante) AS Gol_favor, SUM(Gol_local) AS Gol_contra
                      FROM partido_ok GROUP BY Id_visitante
                  ) AS combined
                  GROUP BY Id_Equipo'''
equipo_gol_fc = duckdb.sql(consulta_f_c).df()

consulta_nombre = '''SELECT DISTINCT Nombre, p.Gol_favor, p.Gol_contra
                     FROM equipo AS e INNER JOIN equipo_gol_fc AS p ON e.Id_Equipo = p.Id_Equipo'''
gol_favor_contra = duckdb.sql(consulta_nombre).df()
gol_favor_contra = gol_favor_contra.sort_values('Gol_contra')

fig, ax = plt.subplots()
gol_favor_contra.plot(x='Nombre', y=['Gol_favor', 'Gol_contra'], kind='barh',
                      label=['Gol a favor', 'Gol en contra'], ax=ax)
ax.set_title('Goles a favor y en contra por equipo')
ax.set_xlabel('Goles')
ax.set_ylabel('')
fig.savefig(img+'goles_favor_contra.png', dpi=100, bbox_inches='tight')
plt.show()

#%% Promedio de goles 
partido_ok = duckdb.query("""
    SELECT * FROM partido
    WHERE Temporada IN ('2011/2012', '2012/2013', '2013/2014', '2014/2015')
""")

goles_local = duckdb.query("SELECT Id_Local as Id_Equipo, Gol_local, Fecha, Temporada FROM partido_ok")
local_x_temporada = duckdb.query("""
    SELECT Id_Equipo, SUM(Gol_local) as Gol_local, temporada
    FROM goles_local GROUP BY Id_Equipo, Temporada
""")

goles_visitante = duckdb.query("SELECT Id_Visitante as Id_Equipo, Gol_visitante, Id_Partido, Fecha, Temporada FROM partido_ok")
visitante_x_temporada = duckdb.query("""
    SELECT Id_Equipo, SUM(Gol_visitante) as Gol_visitante, temporada
    FROM goles_visitante GROUP BY Id_Equipo, Temporada
""")

goles_x_temporada = duckdb.query("""
    SELECT T1.Id_Equipo, (T2.Gol_visitante + T1.Gol_local) as Gol, T1.Temporada
    FROM local_x_temporada as T1 INNER JOIN visitante_x_temporada as T2
    ON T1.Id_Equipo = T2.Id_Equipo AND T1.Temporada = T2.Temporada
""").df()

promedio = duckdb.query("SELECT Id_Equipo, MEAN(Gol) as Promedio FROM goles_x_temporada GROUP BY Id_Equipo").df()

nombres = duckdb.query("""
    SELECT Nombre, Promedio FROM promedio as T1 INNER JOIN equipo as T2 ON T1.Id_Equipo = T2.Id_Equipo
    ORDER BY Promedio DESC
""").df()

fig, ax = plt.subplots()
nombres.plot(x='Nombre', y=['Promedio'], kind='barh', ax=ax, legend=False)
ax.set_title('Promedio de goles por equipo')
ax.set_xlabel('Goles')
ax.set_ylabel('Equipo')
fig.savefig(img+'goles_promedios.png', dpi=100, bbox_inches='tight')
plt.show()

#%% Goles de local vs visitante
consulta_gol = '''SELECT Id_Equipo, SUM(Gol_local) AS Gol_local, SUM(Gol_visitante) AS Gol_visitante
                  FROM (SELECT Id_Local AS Id_Equipo, Gol_local, 0 AS Gol_visitante FROM partido_ok
                        UNION ALL 
                        SELECT Id_Visitante AS Id_Equipo, 0 AS Gol_local, Gol_visitante FROM partido_ok) AS goles
                  GROUP BY Id_Equipo ORDER BY Gol_local DESC'''
gol_local_visitante = duckdb.sql(consulta_gol).df()

consulta_nombre = '''SELECT DISTINCT Nombre, p.Gol_local, p.Gol_visitante FROM equipo_ok AS e
                     INNER JOIN gol_local_visitante AS p ON e.Id_Equipo = p.Id_equipo
                     ORDER BY Gol_local ASC'''
equipo_gol_local_visitante = duckdb.sql(consulta_nombre).df()
equipo_gol_local_visitante['Diferencia'] = equipo_gol_local_visitante['Gol_local'] - equipo_gol_local_visitante['Gol_visitante']
equipo_gol_local_visitante = equipo_gol_local_visitante.sort_values('Diferencia')

fig, ax = plt.subplots()
equipo_gol_local_visitante.plot(x='Nombre', y='Diferencia', kind='barh', ax=ax, legend=False)
ax.set_title('Diferencia de goles convertidos por equipo jugando de local vs visitante')
ax.set_xlabel('Goles')
ax.set_ylabel('')
fig.savefig(img+'goles_convertidos.png', dpi=100, bbox_inches='tight')
plt.show()

#%% Goles por atributos
partido_ok = duckdb.query("""
    SELECT * FROM partido
    WHERE Temporada IN ('2011/2012', '2012/2013', '2013/2014', '2014/2015')
""")

goles_local       = duckdb.query("SELECT Id_Local as Id_Equipo, Gol_local, Fecha, Temporada FROM partido_ok")
local_x_equipo    = duckdb.query("SELECT Id_Equipo, SUM(Gol_local) as Gol_local FROM goles_local GROUP BY Id_Equipo")
goles_visitante   = duckdb.query("SELECT Id_Visitante as Id_Equipo, Gol_visitante, Id_Partido, Fecha, Temporada FROM partido_ok")
visitante_x_equipo = duckdb.query("SELECT Id_Equipo, SUM(Gol_visitante) as Gol_visitante FROM goles_visitante GROUP BY Id_Equipo")

goles_x_equipo = duckdb.query("""
    SELECT T1.Id_Equipo, (T2.Gol_visitante + T1.Gol_local) as Gol
    FROM local_x_equipo as T1 INNER JOIN visitante_x_equipo as T2 ON T1.Id_Equipo = T2.Id_Equipo
""")

Atributos_Constantes = duckdb.query("SELECT Id_Jugador, Altura+Peso as Constantes FROM jugador")
Atributos_Variables  = duckdb.query("""
    SELECT Id_Jugador, SUM(Potencial) + SUM(Velocidad) as Variables FROM atributos GROUP BY Id_Jugador
""")
Suma_Atributos_Jugadores = duckdb.query("""
    SELECT T1.Id_Jugador, (Constantes + Variables) as Atributos
    FROM Atributos_Constantes as T1 INNER JOIN Atributos_Variables as T2 ON T1.Id_Jugador = T2.Id_Jugador
""")
Suma_Atributos_Equipos = duckdb.query("""
    SELECT E.Id_Equipo, SUM(A.Atributos) AS Atributos_Suma
    FROM Suma_Atributos_Jugadores as A
    INNER JOIN plantel_ok as P ON A.Id_Jugador = P.Id_Jugador
    INNER JOIN equipo as E ON P.Id_Equipo = E.Id_Equipo
    GROUP BY E.Id_Equipo;
""").df()

atributos_x_goles = duckdb.query("""
    SELECT T1.Id_Equipo, Atributos_Suma, Gol
    FROM Suma_Atributos_Equipos as T1 INNER JOIN goles_x_equipo as T2 ON T1.Id_Equipo = T2.Id_Equipo
""").df()

fig, ax = plt.subplots()
plt.scatter(atributos_x_goles["Atributos_Suma"], atributos_x_goles["Gol"])
ax.set_title('Goles en función de la suma de atributos')
ax.set_xlabel('Suma de Atributos')
ax.set_ylabel('Goles')
fig.savefig(img+'goles_atributos.png', dpi=100, bbox_inches='tight')
plt.show()