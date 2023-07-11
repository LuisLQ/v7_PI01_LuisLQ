# HENRY Proyecto Integrador 1  
## Luis Alfredo Lopez Quero
PI01 movies LuisLQ - v7  

## ETL  
- realizado con el notebook 'etl_v41'
- Se trabaja con los datasets provistos para desanidar los datos y limpiarlos
- Se obtiene un df pre-procesado que sera utilizado posteriormente por la API, incluido en este repositorio como 'csv'
- nombre: 'MoviesDataset_v41.csv'

## EDA  
- realizado con el notebook 'eda_v1'

## API  
- realizada con FasrAPI
- deploy en Render disponible en: https://movies-v7.onrender.com/docs

## Sistema de recomendación  
- incluido como endpoint en la API
- utiliza una base de datos filtrada para las peliculas con 'popularity > 3', esto debido a la limitación de recursos memoria en la versión free de Render
- para realizarlo se aplicaron técnicas de reducción de la dimensionalidad para generar una matríz de similitud con las siguientes features:
- 1) 'title' y 'overview'
  2) 'collection'
  3) 'genres'
- El modelo elegido es K-vecinos
     

