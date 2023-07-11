"""
uvicorn main_v7:app --reload
uvicorn main_v7:app --host 0.0.0.0 --port 10000
http://127.0.0.1:8000
http://127.0.0.1:8000/docs

"""

import pandas as pd
import numpy as np
import ast
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.neighbors import NearestNeighbors
from fastapi import FastAPI, status, Response

# Filtro para reducir la cantidad de peliculas de la BD
# debido a recursos limitados en Render
# valor = 0 se usa la BD completa
df = pd.read_csv('MoviesDataset_v41.csv')
valor = 5
df_filtrado = df[df['popularity'] > valor]

movies = df_filtrado['title'].tolist()
# concatena 'title' + 'overview' para analizarlo en conjunto
df_filtrado['titleplus'] = df['title'] + " " + df['overview']
titleplus = df_filtrado['titleplus'].tolist()
genres = df_filtrado['genres'].tolist()
collection = df_filtrado['btc_name'].tolist()

n_components = 100

# Vectoriza las sinopsis  (título+overvies) utilizando TF-IDF
vectorizer_synopsis = TfidfVectorizer(stop_words='english')
synopsis_vectors = vectorizer_synopsis.fit_transform(titleplus)
# Reducción de dimensionalidad con LSA
lsa_model = TruncatedSVD(n_components=n_components)
synopsis_vectors_reduced = lsa_model.fit_transform(synopsis_vectors)

# Vectoriza el collection de las películas utilizando TF-IDF
vectorizer_collection = TfidfVectorizer()
collection_vectors = vectorizer_collection.fit_transform(collection)
# Reducción de dimensionalidad con LSA
lsa_model = TruncatedSVD(n_components=n_components)
collection_vectors_reduced = lsa_model.fit_transform(collection_vectors)

# Vectoriza el genero de las películas utilizando TF-IDF
vectorizer_genres = TfidfVectorizer()
genres_vectors = vectorizer_genres.fit_transform(collection)
# Reducción de dimensionalidad con LSA
lsa_model = TruncatedSVD(n_components=n_components)
genres_vectors_reduced = lsa_model.fit_transform(genres_vectors)

# Concatenación de los vectores de características
feature_vectors = np.concatenate((synopsis_vectors_reduced, collection_vectors_reduced, genres_vectors_reduced), axis=1)
column_names = ['Feature_' + str(i+1) for i in range(300)]  # Nombres de las columnas
df_feature_vectors = pd.DataFrame(data=feature_vectors, columns=column_names)
# Generar vectores de características
feature_vectors = df_feature_vectors.values

# Construcción del modelo de vecinos más cercanos
n_neighbors = 6  # Número de vecinos más cercanos a considerar
metric = 'cosine'  # Métrica de similitud (por ejemplo, el coseno de similitud)
model = NearestNeighbors(n_neighbors=n_neighbors, metric=metric)
model.fit(feature_vectors)  # Utiliza las sinopsis reducidas como matriz de características

# Inicializar FastAPI
app = FastAPI()

@app.get('/peliculas_idioma/{idioma}')
def peliculas_idioma(idioma:str):
    # Ingresas el idioma, retornando la cantidad de peliculas producidas
    respuesta = int(df.loc[df['original_language']==idioma]['title'].count())
    return {'idioma': idioma, 'cantidad': respuesta}


@app.get('/peliculas_duracion/{pelicula}')
def peliculas_duracion(pelicula: str):
    # ingresas la pelicula, retornando la duracion y el año
    existe_pelicula = (df['title'] == pelicula).any()
    if existe_pelicula:
        respuesta = df.loc[df['title']==pelicula]['runtime'].values[0]
        anio = int(df.loc[df['title']==pelicula]['release_year'].values[0])
    else:
        pelicula = pelicula + ' no existe en DB'
        respuesta = None
        anio = None
    return {'pelicula': pelicula, 'duracion': respuesta, 'anio': anio}


@app.get('/franquicia/{franquicia}')
def franquicia(franquicia:str):
    # Se ingresa la franquicia, retornando la cantidad de peliculas, 
    # ganancia total y promedio
    cantidad = int(df.loc[df['btc_name']==franquicia]['title'].count())
    ganancia_total = int(df.loc[df['btc_name']==franquicia]['revenue'].sum())
    ganancia_promedio = int(df.loc[df['btc_name']==franquicia]['revenue'].mean())
    return {'franquicia': franquicia, 'cantidad': cantidad, 
            'ganancia_total': ganancia_total, 
            'ganancia_promedio': ganancia_promedio}


@app.get('/peliculas_pais/{pais}')
def peliculas_pais(pais:str):
    # Ingresas el pais, retornando la cantidad de peliculas producidas
    lista_paises = df['countries'].unique().tolist()
    # Analizar las cadenas y convertirlas en listas reales
    lista_convertida = [ast.literal_eval(elemento) for elemento in lista_paises]
    # Aplanar la lista
    paises = [elemento for sublist in lista_convertida for elemento in sublist]
    
    if pais in paises:
        cantidad = int(df.loc[df['countries'].str.contains(pais)]['title'].count())
    else:
        pais = pais + ' no existe en DB'
        cantidad = None
    
    return {'pais': pais, 'cantidad': cantidad}


@app.get('/productoras_exitosas/{productora}')
def productoras_exitosas(productora:str):
    # Ingresas la productora, entregandote el revunue total 
    # y la cantidad de peliculas que realizo
    
    lista_productoras = df['companies'].unique().tolist()
    # Analizar las cadenas y convertirlas en listas reales
    lista_convertida = [ast.literal_eval(elemento) for elemento in lista_productoras]
    # Aplanar la lista
    productoras = [elemento for sublist in lista_convertida for elemento in sublist]

    if productora in productoras:
        cantidad = int(df.loc[df['companies'].str.contains(productora)]['title'].count())
        ganancia_total = int(df.loc[df['companies'].str.contains(productora)]['revenue'].sum())
    else:
        productora = productora + ' no existe en DB'
        cantidad = None
        ganancia_total = None
    
    return {'productora': productora, 
            'revenue_total':ganancia_total,
            'cantidad': cantidad}


@app.get('/get_director/{nombre_director}')
def get_director(nombre_director:str):
    # Se ingresa el nombre de un director debiendo devolver el éxito del mismo medido a través del retorno. 
    # Además, deberá devolver el nombre de cada película con la fecha de lanzamiento, retorno individual, 
    # costo y ganancia de la misma. En formato lista
        
    director = "['" + nombre_director + "']"
    existe = (df['Directors'] == director).any()
    if existe:
        cantidad = int(df.loc[df['Directors'] == director]['title'].count())
        retorno = int(df.loc[df['Directors'] == director]['revenue'].sum())
        peliculas = df.loc[df['Directors'] == director] [['title', 'release_year', 'return', 'budget', 'revenue']].to_dict(orient='records')
    else:
        nombre_director = nombre_director + ' no existe en DB'
        cantidad = None
        retorno = None
        peliculas = None
    
    return {'director': nombre_director, 'retorno_total_director': retorno, 
            'cantidad_peliculas': cantidad, 'peliculas': peliculas}


@app.get('/recomendacion/{titulo}')
def recomendacion(titulo:str):
    # Ingresas un nombre de pelicula y te recomienda las similares en una lista
    existe_pelicula = (df_filtrado['title'] == titulo).any()

    if existe_pelicula:
        movie_index = movies.index(titulo)  # Encuentra el índice de la película ingresada
        
        # Encuentra los vecinos más cercanos
        _, neighbor_indices = model.kneighbors([feature_vectors[movie_index]])
    
        # Crea una lista con los nombres de las películas recomendadas
        recommendations = [movies[i] for i in neighbor_indices[0] if i != movie_index]
    else:
        recommendations = titulo + ' no existe en DB p/ML'

    return {'lista recomendada': recommendations}

""" 
@app.get('/pruebadf/{indice}')
def pruebadf(indice:int):
    # Prueba
    return {'indice': indice, 'pelicula': df['title'][indice]}
""" 

@app.get('/version')
def version():
    # Ingresas un nombre de pelicula y te recomienda las similares en una lista
    return {'version': 'v7', 'componentes': n_components}



