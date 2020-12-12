from datetime import timezone
from datetime import datetime
import json


def date_to_utc(año, mes, dia):
    dt = datetime(año, mes, dia)
    timestamp = dt.replace(tzinfo=timezone.utc).timestamp()
    return float(timestamp) * 1000.0


mapa = """
<!DOCTYPE html>
<html>
<head>
	<script src="https://cdnjs.cloudflare.com/ajax/libs/proj4js/2.3.6/proj4.js"></script>
<script src="https://code.highcharts.com/maps/highmaps.js"></script>
<script src="https://code.highcharts.com/maps/modules/exporting.js"></script>
<script src="https://code.highcharts.com/maps/modules/offline-exporting.js"></script>
<script src="https://code.highcharts.com/mapdata/countries/ec/ec-all.js"></script>

	<title>
		hola
	</title>

	<style type="text/css">
		#container {
    height: 800px; 
    width: 800px; 
    margin: 0 auto; 
}
.loading {
    margin-top: 10em;
    text-align: center;
    color: gray;
}
	</style>
</head>
<body>

	<div id="container"></div>


</body>

	<script type="text/javascript">
	Highcharts.mapChart('container', {

    chart: {
    	plotBorderWidth: 5,
        map: 'countries/ec/ec-all',

       plotBackgroundColor: '#00004d',


    },

    title: {
        text: 'Módulo GPS'
    },

    mapNavigation: {
        enabled: true
    },

    tooltip: {
        headerFormat: '',
        pointFormat: '<b>{point.name}</b><br>Lat: {point.lat}, Lon: {point.lon}',

    },

    series: [

{
        type: 'map',
        name: 'Areas',
        data: [{
            name: "Land",
            color: "#f4e2ba"

            }, 
     ]
  ,
        showInLegend: false
    }
,

{

        // Use the gb-all map with no data as a basemap
        name: 'Basemap',
        borderColor: '#A0A0A0',
        nullColor: 'rgba(200, 200, 200, 0.3)',
        showInLegend: false,

    },
    {
        // Specify points using lat/lon
        type: 'mappoint',
        name: 'Ciudades',

        color: '#00a000',
        data: [
"""
mapa2 = """
]
    }]
});

	</script>



<figure class="highcharts-figure">
  <p class="highcharts-description">
    This demo visualizes a data set with irregular time intervals.
    Highcharts comes with sophisticated functionality for dealing
    with time data, including support for different time zones and
    irregular intervals.
  </p>
</figure>
</html>


"""

mapaIn = """
{
            name: 'Guayaquil',
            lat: -2.19616,
            lon:  -79.88621
        }, {
            name: 'Quito',
            lat:  -0.225219,
            lon:  -78.5248,

        }, {
            name: 'Salinas',
            lat:  -2.22622 ,
            lon:  -80.85873,
            dataLabels: {

                align: 'left',
                x: 5,
                verticalAlign: 'middle',
            }
        }

"""


def list2string(lista):
    st = ""
    for elemento in lista:
        st = st + dict2string(elemento)
    return st


def datos2dict(latitud, longitud, nombre):
    dict = {
        'name': nombre,
        'lat': latitud,
        'lon': longitud
    }
    return dict


def dict2string(dic):
    st = json.dumps(dic)
    return st


def agregar_datos(latitud, longitud, nombre, mapa, mapa2, fd):
    dict = datos2dict(latitud, longitud, nombre)
    str = dict2string(dict)
    mapa = mapa + str
    mapa = mapa + mapa2
    fd.write(mapa)
    fd.close()
    print("Se actualizó ubicación")


f = open('funciona.html', '+w', encoding="utf-8")


def agregar_datos2(latitud, longitud, nombre):
    agregar_datos(latitud, longitud, nombre, mapa, mapa2, f)


agregar_datos2(-2.19616, -79.88621, 'Guayaquil')


def __ag_datos__(json, mapa, mapa2, f):
    mapa = mapa + json
    mapa = mapa + mapa2
    f.write(mapa)
    f.close()


def agg_datosv3(json):
    __ag_datos__(json, mapa, mapa2, f)




