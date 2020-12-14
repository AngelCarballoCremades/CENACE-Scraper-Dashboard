# CENACE Scraper - Dashboard

Data la importancia de la electricidad en cualquier industria de la actualidad, este proyecto falicita el acceso a información sobre el mercado eléctrico en México por medio de la descarga y visualización de datos.

Este proyecto incluye la descarga y actualización automatizada de archivos del CENACE (Scraping) y visualización de los datos por medio de un dashboard hecho con la librería Dash.

Este proyecto construye una base de datos en PostgreSQL haciendo una descarga inicial de archivos (*install_database.py*), la actualiza cada que el usuario lo desea (*update_database.py*) y permite visualizar algunos datos con el dashboard (*dashboard.py*).

La explicación está dividida en 3 partes:
* Extracción de información.
* Actualización de información.
* Visualización de información.


## **Extracción de información**
Por ahora, el programa está hecho para descargar y actualizar:
* Precios PML (MDA y MTR) de los 3 sistemas eléctricos de México.
  * Archivos: *scraper_prices_monthly.py* y *scraper_prices_daily.py*
* Precios PND (MDA y MTR) de los 3 sistemas eléctricos de México.
  * Archivos: *scraper_prices_monthly.py* y *scraper_prices_daily.py*
* Generación de energía Real y Pronóstico
  * Archivos: *scraper_generation_real.py* y *scraper_generation_forecast.py*
* Consumo de Eenergía Real y Pronóstico
  * Archivo: *scraper_consumption.py*

Para realizar todas las descargas debe ejecutar el archivo ***install_database.py*** .

**ANTES** de esto:
* Una carpeta llamada *files* va a ser creada un nivel superior de donde se encuentra el repositorio.
* PostgreSQL debe estar instalado, con el usuario llamado 'postgres' y la contraseña ingresda en el archivo *psql_password.txt*, para cambiar el nombre del usuario deberás ingresar a los archivos correspondientes a realizar el cambio, esto se facilitará en una mejora futura.
* Se creará una base de datos llamada *cenace*, si existe llamada igual se eliminará, en un futuro se va a facilitar el cambio de nombre de la base de datos.

Este archivo ingresará a cada una de las páginas web del CENACE correspondientes y descargará la información desde el 2018 (o después, dependiendo de la disponibilidad de los datos) hasta la última fecha disponible (esto depende del tipo de información).

Después de descargar cada tipo de información, limpia, une y prepara los archivos para ser subidos a la base de datos.

Una vez que termina de descargar y preparar todos los archivos, crea la base de datos *cenace*, cada una de las tablas necesarias y sube los archivos de uno en uno.

Al terminar actualiza a la última fecha disponible los precion PML y PND.


Por ahora, se debe correr manualmente el archivo *cenace_info_file_upload.py*, para agregar a la base de datos la tabla de información de todos los nodos y coordenadas, esto de mejorará en un futuro.


## **Visualización de información**
La visualización se realiza con el archivo *dashboard.py*, es un dashboard realizado con el paquete *Dash* de *Plotly*.
En el archivo *dashboard.py* está la estructura general del dashboard, la generación de gráficas y tablas se hace llamando funciones de:
* Gráficas: *dashboard_graphs.py*
* Tablas y descargas: *dashboard_tables.py*


En el dashboard hay 4 pestañas para explorar la información de la base de datos:
* Generación y Demanda.
* Precios de Energía.
* Localización de Nodos.
* Descarga de Datos.

### Generación y Demanda
En esta pestaña se muestran 3 gráficas distintas:
* Arriba-izquierda: Histórico de generación por día de cada tecnología en el país (se debe dar click en un punto de la gráfica para ver el detalle en horas en la gráfica de la derecha).
* Arriba-derecha: Generación por hora de 20 días (el centro es el punto seleccionado en le gráfica de la izquierda), detalle por tipo de energía.
* Abajo: Histórico de demanda de energía por Zona de Carga, selecciona las zonas de tu interés en el recuadro de la izquierda (Para ver la suma de las zonas, selecciona *MEXICO (PAIS)* únicamente).
![](https://github.com/AngelCarballoCremades/CENACE-Scraper-Dashboard/blob/master/images/tab1_top.PNG)

### Precios de Energía
En esta pestaña se puede analizar el precio de la energía de distintas maneras en las gráficas:
* Dropdowns: Elige el sistema eléctrico, mercado y Zona de Carga que deseas analizar.
* Arriba-izquierda: Histórico del precio promedio diario, distinguido por cada uno de sus componentes de costo (se debe dar click en un punto de la gráfica para ver el detalle en horas en la gráfica de la derecha).
* Arriba-derecha: 'Precio de la energía por hora de 20 días de la Zona de Carga seleccionada (el centro es el punto seleccionado en le gráfica de la izquierda), detalle por componente de costo.
* Abajo-izquierda:
  * Dropdown 1:
    * **(Zona seleccionada) vs Zonas de Carga** Permite analizar la zona de carga seleccionada con otras en el mismo sistema eléctrico (próximamente se podrá analizar con zonas de cualquier sistema).
    * **(Zona seleccionada) vs Nodos Locales** Permite analizar la Zona de Carga seleccionada con los nodos locales que la conforman.
  * Dropdown 2: Tipo de componente de precio a graficar.
    * **Precio Total de Energía.**
    * **Componente de Energía.**
    * **Componente de Pérdidas.**
    * **Componente de Congestión.**
  * Dropdown 3: Sólo habilitado si está seleccionado *Zona vs Nodos Locales* en Dropdown 1.
    * **Valor Real** Grafica los valores reales de cada nodo y la Zona de Carga del componente de precio seleccionado.
    * **Diferencia vs Zona de Carga** Grafica la diferencia en porcentaje de cada nodo local vs la zona de carga por día.
  * Dropdown 4: Sólo habilitado si está seleccionado *Zona vs Zonas de Carga* en Dropdown 1.
    * Selecciona las Zonas de Carga contra las que quieres comparar la Zona de Carga seleccionada.
  * **Obtener más información** Genera una tabla con información extra de la zona y nodos/zonas analizadas, esta tabla es descargable.
* Abajo-derecha: Gráfica resultado de lo seleccionado en los dropdowns.
![](https://github.com/AngelCarballoCremades/CENACE-Scraper-Dashboard/blob/master/images/tab2_top.PNG)
![](https://github.com/AngelCarballoCremades/CENACE-Scraper-Dashboard/blob/master/images/tab2_bottom.PNG)

### Localización de Nodos
Esta pestaña te permite localizar los nodos más cercanos a una coordenada deseada.
Por seguridad nacional, la ubicación exacta de los nodos locales no está disponible al público. Las ubicaciones mostradas son el centroide aproximado del municipio al que pertenecen los nodos.
Las coordenadas de los municipios se calculan en el archivo *cenace_info_file_upload.py*, es a partir de un archivo .shp del INEGI con las geometrías de todos los municipios del país.

En el mapa se deben ingresar las coordenadas deseadas y el número de nodos que se buscar mínimo alrededor. (También se puede cambiar el tipo de mapa mostrado).
![](https://github.com/AngelCarballoCremades/CENACE-Scraper-Dashboard/blob/master/images/tab3_top.PNG)

Una vez que se realiza la búsqueda, se puede seleccionar uno de los círculos azules para obtener información detallada de los nodos de ese municipio (o se selecciona el círculo amarillo para información de todos los municipios mostrados).

La tabla resultante se puede descargar.
![](https://github.com/AngelCarballoCremades/CENACE-Scraper-Dashboard/blob/master/images/tab3_bottom.PNG)

### Descarga de Datos
Esta pestaña está diseñada para personas que no tienen conocimiento de SQL, aquí puedes seleccionar y descargar información de la base de datos fácilmente, antes de descargar presiona el botón *Vista Previa* para asegurarte que seleccionaste la información deseada y luego presiona *Descargar* para generar el archivo *.csv*.

Toda la informcaión que se descarga aquí es información por hora.

Descargas disponibles:
* **Generación** Permite descargar información de generación REAL y PRONÓSTIVO.
* **Demanda** Permite descargar información de demanda REAL y PRONÓSTIVO de cada Zona de Carga (si se quiere la suma de todas las zonas se puede seleccionar *MEXICO (PAIS)*)
* **Precios** Permite descargar información de precios de energía MTR y MDA. Ya sea de una o varias Zonas de Carga o uno o varios Nodos Locales de alguna Zona de Carga.
* **SQL** Permite hacer comandos en lenguaje SQL a la base de datos sin necesidad de salir del Dashboard, se debe tener cuidado de no pedir tablas muy grandes, para no llenar la memoria del explorador y la computadora, no está limitado el número de filas.
![](https://github.com/AngelCarballoCremades/CENACE-Scraper-Dashboard/blob/master/images/tab4_tab1.PNG)
![](https://github.com/AngelCarballoCremades/CENACE-Scraper-Dashboard/blob/master/images/tab4_tab4.PNG)

### Botones superiores
* **Actualizar BD** Ejecuta el script *update_database.py*
* **Conectar de nuevo con SQL** Hay ocasiones en que se realizan comandos de SQL mal ejecutados y en momentos es requerido un ROLLBACK, este botón lo ejecuta.


Todas las descargas del dashboard están dentro de la carpeta ../files/descargas
