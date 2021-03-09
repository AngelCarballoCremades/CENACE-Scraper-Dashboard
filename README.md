# Mexico's Energy Market ETL & Dashboard

Online webpage showing dashboard: [](https://mexico-energy-dashboard.herokuapp.com/)

This project scrapes, cleans and loads data to a PostgreSQL database, keeps the data up to date and displays the information in a Dashboard made with Plotly's Dash.

The information can be download to a local database or a connection can be made to an AWS RDS instance (default).

## Setup & Run (Online database)
1. Install: python 3.8 or higher (Developed initially in 3.8.5), Virtualenv
2. ./venv/bin/activate #Activate environment 
3. pip install -r requirements.txt #Install required packages
4. python dashboard.py #Run dashboard file locally
5. Open browser and go to http://127.0.0.1:8050/


## Setup & Run (Local database)
1. Install: Postgres 13, Python 3.8 or higher (Developed initially in 3.8.5), Virtualenv.
2. ./venv/bin/activate # Activate environment.
3. pip install -r requirements.txt # Install required packages.
4. Write Postgres credentials in psql_password.txt file as follows:
	localhost
	user
	password
	port
4. python install_database.py # Download data, prepare it and upload to PostgreSQL database.
5. python dashboard.py # Run dashboard file locally.
6. Open browser and go to http://127.0.0.1:8050/
7. python update_database.py # Keeps the database up to date, best if run after 10 pm (Mexico city time)

## Important Information
* Postgres 13 is used in this project.
  * A database called '*cenace*' is created (if it already exists it will erase it and create a new one. Be careful!).
* Folder named *files* is created one level above the project folder.
  * All downloaded files will be there in it's respective folder.
  * Normally you shouldn't mess with files in here unless you want to check original downloaded files or download again the entire database.


### Data Downloaded
Data downloaded includes energy generation, consumption and prices.

* Energy Generation
  * [Hourly energy generation forecast](https://www.cenace.gob.mx/Paginas/SIM/Reportes/H_PronosticosGeneracion.aspx?N=245&opc=divCssPronosticosGen&site=Pron%C3%B3sticos%20de%20Generaci%C3%B3n%20Intermitente&tipoArch=C&tipoUni=ALL&tipo=All&nombrenodop=) (solar and wind only), available every day
  * [Hourly energy generation real data](https://www.cenace.gob.mx/SIM/VISTA/REPORTES/EnergiaGenLiqAgregada.aspx) (only liquidation #0), available every month
* Energy Consumption
  * [Hourly zone (Zona de Carga) energy consumption forecast](https://www.cenace.gob.mx/Paginas/SIM/Reportes/PronosticosDemanda.aspx), available every day
  * [Hourly zone (Zona de Carga) energy consumption real data](https://www.cenace.gob.mx/Paginas/SIM/Reportes/EstimacionDemandaReal.aspx) (only liquidation #0), available every day
* [Energy Prices](https://www.cenace.gob.mx/Paginas/SIM/Reportes/PreciosEnergiaSisMEM.aspx)
  * Hourly nodal prices (PML)
    * Forecasted price (MDA)
    * Real price (MTR)
  * Hourly zone prices (PND)
    * Forecasted price (MDA)
    * Real price (MTR)

If locally hosted database is used, the information is initially downloaded in the correct folder (for example: ../files/generation/real), then processed and prepared for being uploaded to the database.
Joined price files are limited to 1 GB, so several files may be created for one type of data (PostgreSQL has a 1 GB limit for uploaded files). It is done automatically.

## Data Extraction - Updating Information
New information is available every day depending on the type of data. To download the information gap between the last update (or first intallation) and last data available online run ***update_database.py***. Last date available will be searched automatically in every database's table and corresponding files (if new files are available) downloaded, transformed and uploaded.
The AWS database will be updated every week aprox.

## Visualization
Visualization of some of the information is done via a Dashboard made with the package Dash (from Plotly).
This dashboard creates interactive graphs whith information from the database.
The Dashboard has 4 tabs:
* Generation & Consumption (Generación y Demanda)
* Energy Prices (Precios de Energía)
* Nodes Location (Localización de Nodos)
* Data Download (Descarga de Datos)

### Generation & Consumption
There are 3 different graphs in this tab:
* Top-left: Daily generation data divided by technology type (Click on a plotted line in this graph to interact with top-right graph)
* Top-right: Hourly generation, 20 day span (center point is day selected in top-left graph), divided by technology type
* Bottom: Energy consumption by zone (Zona de Carga), select different zones to plot from the dropdown to the left (In order to plot the sum of all the zones, select *MEXICO (PAIS)* only)
![](https://github.com/AngelCarballoCremades/CENACE-Scraper-Dashboard/blob/master/images/tab1_top.PNG)

### Energy Prices
This tab allows you to analyze energy price in different ways:
* Top dropdowns: Choose Mexico's electric system, market and zone to be analyzed.
* Top-left: Daily average energy price in selected zone, divided by price component (Click on a plotted line in this graph to interact with top-right graph)
* Top-right: Hourly energy price from selected zone, 20 day span (center point is day selected in top-left graph), divided by price component
* Bottom-left:
  * Dropdown 1:
    * **(Zona seleccionada) vs Zonas de Carga** - Selected zone vs other zones - Allows analyzing selected zone with any other zone inside it's electrical system
    * **(Zona seleccionada) vs Nodos Locales** - Selected zone vs nodes - Allows analyzing selected zone with every node inside it
  * Dropdown 2: Price component to be analyzed
    * **Precio Total de Energía** - Total Energy Price
    * **Componente de Energía** - Energy Component
    * **Componente de Pérdidas** - Loss Component
    * **Componente de Congestión** - Congestion Component
  * Dropdown 3: Only clickable if *(Zona seleccionada) vs Nodos Locales* selected in Dropdown 1
    * **Valor Real** - Real Value - Plots daily value of selected energy component from the selected zone and all of its nodes
    * **Diferencia vs Zona de Carga** - Difference vs Zone - Plots daily difference (%) between selected zone and its nodes
  * Dropdown 4: Only clickable if *(Zona seleccionada) vs Zonas de Carga* is selected in Dropdown 1
    * Select zones to plot with the selected zone and analyze selected energy component
  * **Obtener más información** - Get more information - Generates a table with extra information from selected zone and nodes or zones plotted
* Bottom-right: Plot showing information selected in bottom-left dropdowns
![](https://github.com/AngelCarballoCremades/CENACE-Scraper-Dashboard/blob/master/images/tab2_top.PNG)
![](https://github.com/AngelCarballoCremades/CENACE-Scraper-Dashboard/blob/master/images/tab2_bottom.PNG)

### Nodes Location
In this tab you can find nodes close to a given coordinate.
Due to nationat security issues, exact location of nodes is not made public. Locations shown are the calculated centroid of the node's municipality.
Minicipalities' coordinates are calculated via ***cenace_info_file_upload.py***, it uses a .shp file from INEGI containing Mexico's detailed geometry.

Coordinates showld be entered in respective input box and select a number of nodes to be displayed (type of map shown can also be selected).
![](https://github.com/AngelCarballoCremades/CENACE-Scraper-Dashboard/blob/master/images/tab3_top.PNG)

Once a result has been shown, select one of the blue circles to get extra information from the nodes of that municipality (or select the yellow circle to get extra information from all resulting nodes).

The table can be downloaded.
![](https://github.com/AngelCarballoCremades/CENACE-Scraper-Dashboard/blob/master/images/tab3_bottom.PNG)

### Data Download
this tab is designed for people not having enough SQL knowledge. Here information can be selected and downloaded for further analysis. Before clicking download button (*Descargar*), click preview button (*Vista Previa*) so you are sure that is the information wanted. Downloads should be created in default downloads folder.

**Information downloaded in this tab is hourly data.**

Available data to download:
* **Generación** - Generation - Allows download of REAL and FORECAST (Pronóstico) generation data
* **Demanda** - Consumption - Allows download of REAL and FORECAST of every zone (In order to get the sum of all the zones, select *MEXICO (PAIS)* only)
* **Precios** - Prices - Allows download from markets MTR & MDA, zone selected can be one or more. Instead of zones, nodes can be selected too (nodes in the list are the ones belonging to selected zones)
![](https://github.com/AngelCarballoCremades/CENACE-Scraper-Dashboard/blob/master/images/tab4_tab1.PNG)
![](https://github.com/AngelCarballoCremades/CENACE-Scraper-Dashboard/blob/master/images/tab4_tab4.PNG)