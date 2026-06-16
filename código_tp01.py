
# Importamos bibliotecas
import pandas as pd
import duckdb
import numpy as np 

#%%===========================================================================
# Importamos los datasets que vamos a utilizar en este programa, los limpiamos para que no tengan NaN
#=============================================================================

carpeta = r'C:\Users\Nt\Desktop\Carrera\Laboratorio de Datos\\'

equipo_e = pd.read_csv(carpeta+'enunciado_equipos.csv').dropna()

liga_e = pd.read_csv(carpeta+'enunciado_liga.csv').dropna()

partido_e = pd.read_csv(carpeta+'enunciado_partidos.csv').dropna() #Este es el dataset más importante, permite relacionar casi todas las entidades

jugador_e = pd.read_csv(carpeta+'enunciado_jugadores.csv').dropna()

atributos_e = pd.read_csv(carpeta+'enunciado_jugadores_atributos.csv').dropna()

#%%===========================================================================
# Creeamos las tablas 
#=============================================================================
#%% EQUIPO 

#Eliminamos las columnas que no queremos 
equipo_ok = equipo_e.drop(['team_fifa_api_id','team_short_name'], axis=1)

#Usando el dataset partido, creamos un DF donde en una columna estén los equipos locales y visitantes y en otra su liga 
equipo_liga = pd.melt(partido_e, 
                        id_vars=['league_id', 'season'], 
                        value_vars=['home_team_api_id', 'away_team_api_id'],
                        value_name='team_id').drop(columns='variable')

# Al DF creado, le eliminamos los duplicados 
equipo_liga = equipo_liga[['team_id', 'league_id']].drop_duplicates()

#Usamos SQL unir el DF creado con el dataset de partidos

consulta_equipo= '''SELECT *
                    FROM equipo_liga
                    INNER JOIN equipo_ok
                    ON team_id = team_api_id'''
equipo_0 = duckdb.sql(consulta_equipo)

#Creamos la tabla final 

consulta = '''SELECT team_id AS Id_Equipo, league_id AS Id_Liga, team_long_name AS Nombre FROM equipo_0'''
equipo = duckdb.sql(consulta).df()

#Guardamos la tabla
equipo.to_csv(carpeta+'equipo.csv', index=False) 

#%% LIGA 

consulta_liga = '''SELECT country_id as Id_Liga, name FROM liga_e '''

liga = duckdb.sql(consulta_liga).df()

#Guardamos la tabla
liga.to_csv(carpeta+'liga.csv')

#%% Partido

#Creamos una tabla solo con los atributos necesarios
consulta_partido = '''SELECT match_api_id AS Id_Partido, date AS Fecha, season AS Temporada, home_team_api_id AS Id_Local,
                       away_team_api_id AS Id_Visitante, home_team_goal AS Gol_local, away_team_goal AS Gol_visitante 
                       FROM partido_e'''

partido_ok = duckdb.sql(consulta_partido).df()

#Necesitamos crear una columna con el resultado del partido, así que restamos las columnas del gol local y visitante
partido_ok['Valor'] = partido_ok['Gol_local']-partido_ok['Gol_visitante']

#Definimos un clasificador para los valores de la resta anterior. El resultado será el del equipo local
def clasificador(x):
    if x > 0:
        return 'Ganado'
    elif x < 0:
        return 'Perdido'
    else:
        return 'Empate'

partido_ok['Resultado'] = partido_ok['Valor'].apply(clasificador)

partido = partido_ok.drop(['Valor'],axis=1)

#Guardamos la tabla
partido.to_csv(carpeta+'partido.csv',index = False)
                      

#%% PLANTEL A LO LARGO DE LAS TEMPORADAS

# Creamos un DF con los jugadores locales, su id y equipo

local_0 = pd.melt(partido_e, 
                id_vars=['match_api_id', 'home_team_api_id','season'],
                value_vars=[f'home_player_{i}' for i in range(1, 12)],
                value_name='Id_Jugador').drop(columns='variable') 

local = duckdb.sql('''SELECT home_team_api_id AS Id_Equipo, Id_Jugador, match_api_id AS Id_partido, season AS Temporada FROM local_0 ''').df()

# Idem jugadores visitantes

visitante_0 = pd.melt(partido_e, 
                id_vars=['match_api_id', 'away_team_api_id','season'],
                value_vars=[f'away_player_{i}' for i in range(1, 12)],
                value_name='Id_Jugador').drop(columns='variable') 

visitante = duckdb.sql('''SELECT away_team_api_id AS Id_Equipo, Id_Jugador, match_api_id AS Id_partido,season AS Temporada FROM visitante_0 ''').df()

#Uno los DF y elimino duplicados
jugadores = pd.concat([local, visitante], ignore_index=True) 

plantel_0 = jugadores[['Id_Jugador', 'Id_Equipo','Temporada']].drop_duplicates()

plantel = plantel_0.sort_values(by=['Id_Equipo','Temporada'])

plantel.to_csv(carpeta+'plantel.csv',index = False)

#%% LIGA ESPAÑOLA

#Filtramos los equipos de la liga española
equipo_españa = duckdb.sql('''SELECT * FROM equipo WHERE Id_Liga =21518''').df()

#Filtramos los planteles que pertenecen a los equipos españoles
plantel_españa_0 = duckdb.sql('''SELECT * FROM plantel INNER JOIN equipo_españa ON plantel.Id_Equipo =equipo_españa.Id_Equipo''').df()

plantel_españa = plantel_españa_0.drop(['Id_Equipo_1','Id_Liga', 'Nombre'],axis=1)

#Filtramos los partidos que se jugaron entre equipos españoles
partidos_españa_0 = duckdb.sql('''SELECT * FROM partido INNER JOIN equipo_españa ON Id_Local = Id_Equipo ''').df()

partidos_españa = partidos_españa_0.drop(['Id_Equipo', 'Nombre','Id_Liga'],axis=1)

#Guardo las tablas que usaré para la liga española
partidos_españa.to_csv(carpeta+'partido_esp.csv',index = False)
plantel_españa.to_csv(carpeta+'plantel_esp.csv',index = False)
equipo_españa.to_csv(carpeta+'equipo_esp.csv',index = False)





local_0 = pd.melt(partido_e, 
                id_vars=['match_api_id', 'home_team_api_id','season'],
                value_vars=[f'home_player_{i}' for i in range(1, 12)],
                value_name='Id_jugador').drop(columns='variable') 

local = duckdb.sql('''SELECT home_team_api_id AS Id_Equipo, Id_jugador, match_api_id AS Id_partido, season AS Temporada FROM local_0 ''').df()

# Idem jugadores visitantes

visitante_0 = pd.melt(partido_e, 
                id_vars=['match_api_id', 'away_team_api_id', 'season'],
                value_vars=[f'away_player_{i}' for i in range(1, 12)],
                value_name='Id_jugador').drop(columns='variable') 

visitante = duckdb.sql('''SELECT away_team_api_id AS Id_Equipo, Id_jugador, match_api_id AS Id_partido, season AS Temporada FROM visitante_0 ''').df()

#Uno los DF y elimino duplicados
jugadores = pd.concat([local, visitante], ignore_index=True) 

plantel_0 = jugadores[['Id_jugador','Id_Equipo', 'Temporada']].drop_duplicates()

plantel = plantel_0.sort_values(by=['Id_Equipo','Temporada'])








