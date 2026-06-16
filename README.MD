# Análisis Liga Española ⚽

Análisis exploratorio de la **Liga Española de Fútbol** entre las temporadas 2011/2012 y 2014/2015, enfocado en rendimiento de equipos y jugadores a partir de datos de partidos, planteles y atributos.

---

## Estructura del proyecto

```
Analisis-liga-espa-ola/
│
├── análisis_tp01.py        # Script principal con consultas y visualizaciones
│
├── imagenes/               # Gráficos generados automáticamente
│   ├── goles_favor_contra.png
│   ├── goles_promedios.png
│   ├── goles_convertidos.png
│   └── goles_atributos.png
│
└── README.md
```

---

## Temporadas analizadas

Se seleccionaron las temporadas **2011/2012 a 2014/2015** como criterio de consistencia: son las que presentan menor variación en el número de partidos jugados entre sí (diferencia menor a 20 partidos por temporada).

---

## Dependencias

```
pandas
duckdb
numpy
matplotlib
seaborn
```

Instalación:
```bash
pip install pandas duckdb numpy matplotlib seaborn
```

---

## Consultas realizadas

- **Equipo más ganador** en el período completo → FC Barcelona
- **Equipo más perdedor por año** → Granada CF (2012), Rayo Vallecano (2013), UD Almería (2014), Levante UD (2015)
- **Equipo con más empates en 2015** → RC Deportivo de La Coruña
- **Equipo con más goles a favor** → Real Madrid CF
- **Equipo con mayor diferencia de goles** → FC Barcelona
- **Jugador que perteneció a más equipos** → Tono (4 equipos)
- **Jugador con menor variación de potencial** → Matias Autret

---

## Visualizaciones

### Goles a favor y en contra por equipo

<img src="imagenes/goles_favor_contra.png" width="60%">

La mayoría de los equipos recibió más goles de los que convirtió, lo que sugiere un nivel defensivo general bajo en la liga. Sin embargo, este gráfico no considera que no todos los equipos jugaron la misma cantidad de temporadas, por lo que equipos como SD Eibar aparecen con pocos goles en contra simplemente por haber jugado menos partidos. Al normalizar por temporadas jugadas, el FC Barcelona resulta ser el equipo con menos goles en contra.

---

### Promedio de goles por equipo

<img src="imagenes/goles_promedios.png" width="60%">

El Real Madrid CF y el FC Barcelona tienen un promedio de goles muy superior al resto de los equipos, lo que refleja su superioridad ofensiva sostenida a lo largo de las cuatro temporadas. Esta diferencia es un indicador claro de por qué ambos equipos dominaron la liga en el período analizado.

---

### Diferencia de goles convertidos jugando de local vs visitante

<img src="imagenes/goles_convertidos.png" width="60%">

En la mayoría de los equipos la diferencia es positiva, lo que indica que convirtieron más goles jugando de local que de visitante. El Real Madrid CF es el equipo con mayor diferencia, seguido por el Atlético de Madrid y el FC Barcelona. Al normalizar por temporadas jugadas se mantiene esta tendencia, lo que sugiere que la localía tiene un impacto real en el rendimiento ofensivo de los equipos.

---

### Goles en función de la suma de atributos por equipo

<img src="imagenes/goles_atributos.png" width="60%">

Se observa una tendencia lineal positiva entre la suma de atributos de los jugadores de un equipo y los goles convertidos: equipos con mejores jugadores tienden a convertir más goles. Sin embargo, esta relación no es garantía: Atlético Madrid y Valencia CF presentan atributos altos pero un número de goles relativamente bajo. Los outliers claros son Real Madrid CF y FC Barcelona. Al normalizar por temporadas jugadas y cantidad de jugadores, la tendencia se mantiene pero con menor pendiente.

---

## Fuente de datos

Datos de la Liga Española extraídos de bases de datos de rendimiento deportivo (SoFIFA).