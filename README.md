# CENACE scraper
Este proyecto facilita la descarga, actualización y unión de archivos energéticos del CENACE.

## Información descargable
* Sistemas Interconectados
	* **SIN**: Sistema Interconectado Nacional
	* **BCS**: Sistema Interconectado Baja California Sur
	* **BCA**: Sistema Interconectado Baja California
* Nodos
	* **PND** Precios de Nodos Distribuidos
	* **PML** Precios Marginales Locales
* Mercados
	* **MDA** Mercado en Día de Adelanto
	* **MTR** Mercado en Tiempo Real
 
Para mayor información visita las [bases del mercado](https://www.cenace.gob.mx/Paginas/SIM/BasesMercado.aspx)

# Instrucciones
Hay 3 archivos *.py*:
* *monthly_download.py*
* *daily_download.py*
* *join_files.py*

### *monthly_download.py*
Crea una base de datos desde cero con la información del año actual y el año anterior de todos los sistemas, nodos y mercados.
Debería utilizarse sólo inicialmente.

### *join_fles.py*
Junta los archivos descargados en *monthly_download.py* y crea archivos *.cvs* por sistema, nodo y sistema.

### *daily_download.py* 
Analiza la última fecha presente en los *.csv* creados con *monthly_download.py* y utiliza la API del cenace ([Servicio Web PEND](https://www.cenace.gob.mx/DocsMEM/2020-01-14%20Manual%20T%C3%A9cnico%20SW-PEND.pdf)) para actualizar la información a la última fecha disponible, actualiza los archivos *.csv* .

Falta agregar la API de PML [Servicio Web PML](https://www.cenace.gob.mx/DocsMEM/2020-01-14%20Manual%20T%C3%A9cnico%20SW-PML.pdf), no se ha realizado por el peso de los archivos (supera los 2 GB en *.csv*), se requieren modificaciones menores ya que el método de invocación es prácticamente el mismo.
