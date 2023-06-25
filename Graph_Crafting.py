import networkx as nx
from networkx.algorithms.community.label_propagation import label_propagation_communities
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import NearestNeighbors
from Data_Processing import get_ingredients, get_reviewers_id, get_recipe_id
from math import log

class NutritionalRecommender:
    def __init__(self, nutritional_df, nutritional_data_columns):
        self.original_nutritional_df = nutritional_df
        self.nutritional_df = nutritional_df.copy()
        self.nutritional_data_columns = nutritional_data_columns
        
        self.scaler = MinMaxScaler()
        self.nutritional_df[self.nutritional_data_columns] = self.scaler.fit_transform(self.nutritional_df[self.nutritional_data_columns])
        
        self.knn = NearestNeighbors(metric='euclidean')
        self.knn.fit(self.nutritional_df[self.nutritional_data_columns])

    def find_closest_recipes(self, recipe_id, k):
        input_recipe = self.nutritional_df.loc[self.nutritional_df["RecipeId"] == recipe_id, self.nutritional_data_columns]
        distances, indices = self.knn.kneighbors(input_recipe, n_neighbors=k+1)
        
        closest_indices = indices[0][1:]
        return self.original_nutritional_df.iloc[closest_indices]

def main():
    pass


def create_recipe_graph():
    """
    Crea un grafo dirigido que representa la relación de pertenencia entre las recetas y sus ingredientes.
    Lee los datos de un archivo de formato parquet y crea el grafo utilizando la biblioteca NetworkX.
    Guarda el grafo en un archivo de formato GraphML.
    """
    
    df_recipes = pd.read_parquet("cleaned_recipes.parquet")
    G = nx.DiGraph()
    
    for n, recipe in df_recipes.iterrows():
        ingredients_set = get_ingredients(recipe)
        ingredients = list(ingredients_set)
        for i in range(len(ingredients)):
            G.add_edge(recipe["Name"], ingredients[i])
    
    nx.write_graphml(G, "Recipes.graphml")


def create_ingredients_graph():
    """
    Crea un grafo no dirigido que representa la relación entre los ingredientes de cada receta.
    Lee los datos de un archivo de formato parquet y un archivo GraphML que contiene el grafo dirigido
    que representa la relación entre las recetas y sus ingredientes. 
    Luego, calcula el PMI entre cada par de ingredientes y agrega una arista entre ellos con PMI como peso.
    Devuelve el grafo no dirigido resultante y lo guarda en un archivo de formato GraphML.
    """

    df_recipes = pd.read_parquet("cleaned_recipes.parquet")
    Recipe_Graph = nx.read_graphml("Recipes.graphml")
    G = nx.Graph()
    
    recipes_total = len(df_recipes.index)
    
    for _, recipe in df_recipes.iterrows():
        ingredients_set = get_ingredients(recipe)
        ingredients = list(ingredients_set)
        for i in range(len(ingredients)-1):
            for j in range(i+1,len(ingredients)):
                if G.has_edge(ingredients[i],ingredients[j]):
                    pass    
                else:
                    PMI = calculate_PMI(Recipe_Graph, ingredients[i], ingredients[j], recipes_total)
                    G.add_edge(ingredients[i], ingredients[j], weight = PMI)
    
    nx.write_graphml(G, "Ingredients.graphml")


def create_reviewers_graph():
    """
    Crea un grafo que representa las relaciones entre las recetas y sus autores. 
    La función carga dos archivos en formato parquet: "cleaned_recipes.parquet" y "cleaned_reviews.parquet".
    A continuación, filtra las recetas que tienen más de 10 reseñas y para cada receta, identifica a los autores de esas reseñas.
    Luego, compara los autores con los de las demás recetas y agrega una arista entre dos recetas si tienen más de 5 autores en común.
    Guarda el grafo en un archivo de formato GraphML.
    """

    df_recipes_all = pd.read_parquet("cleaned_recipes.parquet")
    df_reviews = pd.read_parquet("cleaned_reviews.parquet")
    G = nx.Graph()

    df_recipes_all = df_recipes_all[df_recipes_all["ReviewCount"] > 10]
    df_recipes_all["Reviewers"] = df_recipes_all["RecipeId"].apply(lambda x: get_reviewers_id(x, df_reviews))
    print(df_recipes_all["Reviewers"])
    for n, recipe in df_recipes_all.iterrows():
        df_recipes = df_recipes_all.copy()
        df_recipes["AuthorsMatch"] = df_recipes["Reviewers"].apply(lambda x: len(x.intersection(recipe["Reviewers"])) > 5)
        df_recipes = df_recipes.loc[df_recipes["AuthorsMatch"] == True]
        for m, match in df_recipes.iterrows():
            if recipe["RecipeId"] != match["RecipeId"]:
                G.add_edge(recipe["Name"], match["Name"])
    nx.write_graphml(G, "Reviewers.graphml")


def calculate_ingredient_similarity(df_recipes, recipe_id):
    """
    Calcula la similitud entre los ingredientes de una receta y todas las demás recetas en el conjunto de datos.
    La función utiliza el grafo no dirigido que representa la relación de distancias entre los ingredientes de
    las recetas para calcular la similitud.

    Args:
    - df_recipes: DataFrame que contiene información sobre todas las recetas del conjunto de datos.
    - recipe_id: El ID de la receta para la que se desea calcular la similitud.

    Returns:
    - recipe_factor_max: Las 10 recetas más similares a la receta especificada, con su factor de similitud añadido.
    """

    Ingredients_Graph = nx.read_graphml("Ingredients.graphml")

    recipe = df_recipes.loc[df_recipes['RecipeId'] == recipe_id].iloc[0]

    df_recipes["factor"] = df_recipes.apply(lambda x: shortest_path_factor(Ingredients_Graph, recipe, x), axis = 1)
    recipe_factor_max = df_recipes.sort_values("factor", ascending = False)
    return recipe_factor_max[0:9]


def calculate_nutritional_similarity(df_recipes, recipe_id):
    """
    Calcula las recetas que tienen una mayor similitud nutricional con una receta dada.
    La función utiliza un subconjunto de columnas del DataFrame que contiene información
    sobre todas las recetas del conjunto de datos para calcular la similitud nutricional.
    Luego, utiliza un recomendador nutricional basado en el método NearestNeighbors con distancia euclideana
    tras escalar la data con MinMaxScaler para encontrar las 100 recetas con mayor similitud nutricional a la receta dada.

    Args:
    - df_recipes: DataFrame que contiene información sobre todas las recetas del conjunto de datos.
    - recipe_id: El ID de la receta para la que se desea calcular la similitud nutricional.

    Returns:
    - nutritional_sim_df: Un DataFrame con información sobre las 100 recetas con mayor similitud nutricional.
    - recipe_id: El ID de la receta para la que se está calculando la similitud nutricional.
    """

    nutritional_columns = ["RecipeId", "Name", "Calories", "FatContent", "SaturatedFatContent", "CholesterolContent", 
                           "SodiumContent", "CarbohydrateContent","FiberContent", "SugarContent", "ProteinContent", 
                           "RecipeServings"]
    nutritional_df = df_recipes[nutritional_columns]
    nutritional_data_columns = ["Calories", "FatContent", "SaturatedFatContent", "CholesterolContent", "SodiumContent",
                      "CarbohydrateContent", "FiberContent", "SugarContent", "ProteinContent"]
    nutritional_df.loc[:,nutritional_data_columns] = nutritional_df.loc[:,nutritional_data_columns].div(nutritional_df["RecipeServings"], axis=0)
    nutritional_df.drop("RecipeServings", axis=1)
    recommender = NutritionalRecommender(nutritional_df, nutritional_data_columns)
    nutritional_sim_df = recommender.find_closest_recipes(recipe_id, k = 100)
    return nutritional_sim_df, recipe_id


def calculate_reviewers_similarity(df_recipes, recipe_id):
    G = nx.read_graphml("Reviewers.graphml")
    df = pd.DataFrame()

    recipe = df_recipes.loc[df_recipes['RecipeId'] == recipe_id].iloc[0]
    neighbors = G.neighbors(recipe["Name"])
    for neighbor in neighbors:
        fila = df_recipes.loc[df_recipes["Name"] == str(neighbor)].iloc[0]
        fila_df = fila.to_frame().T
        df = pd.concat([df, fila_df], ignore_index=True)
    return df, recipe_id



def calculate_PMI(Recipe_Graph, A_ingredient, B_ingredient, total):
    """
    Calcula el puntaje de Pointwise Mutual Information (PMI) entre dos ingredientes A y B.
    Para ello, se utiliza un grafo que representa las relaciones entre los ingredientes y las recetas.
    El método predecessors otorgará todas las recetas a las que pertenezca un ingrediente. 

    Args:
    - Recipe_Graph: un objeto Grafo que representa las relaciones entre los ingredientes y las recetas.
    - A_ingredient: el nombre del primer ingrediente.
    - B_ingredient: el nombre del segundo ingrediente.
    - total: el número total de recetas.

    Returns:
    - PMI: el puntaje de Pointwise Mutual Information (PMI) entre los dos ingredientes A y B.
    """

    Pa = len(list(Recipe_Graph.predecessors(A_ingredient))) / total
    Pb = len(list(Recipe_Graph.predecessors(B_ingredient))) / total
    Pab = len(set(Recipe_Graph.predecessors(A_ingredient)) & set(Recipe_Graph.predecessors(B_ingredient))) / total
    PMI = log(Pab/(Pa*Pb))
    return PMI


def shortest_path_factor(G, A_Recipe, B_Recipe) -> float:
    """
    Calcula un factor de similitud entre dos recetas A y B basado en la distancia más corta entre los ingredientes que comparten.

    Para calcular el factor de similitud, la función obtiene la lista de ingredientes de las recetas A y B.
    A continuación, calcula la distancia más corta entre cada par de ingredientes que comparten las dos recetas utilizando la función
    "nx.shortest_path_length" de la biblioteca NetworkX.
    Si no se puede encontrar un camino entre dos ingredientes, se descarta similitud en el par de recetas.
    Finalmente, la función calcula el factor de similitud como el inverso de la media de las distancias más cortas entre los ingredientes
    que comparten las dos recetas.

    Args:
    - G: un objeto Grafo que representa las relaciones entre los ingredientes.
    - A_Recipe: un objeto que representa la receta A.
    - B_Recipe: un objeto que representa la receta B.

    Returns:
    - factor: un número de punto flotante que indica el factor de similitud entre las dos recetas A y B.
    Si no hay conexión posible entre ingredientes de las dos recetas, el factor será -1.
    """

    if A_Recipe["RecipeId"] != B_Recipe["RecipeId"]:
        A_ingredients = get_ingredients(A_Recipe)
        B_ingredients = get_ingredients(B_Recipe)
        shortest_paths =  []

        for i in A_ingredients:
            for j in B_ingredients:
                try:
                    shortest_paths.append(nx.shortest_path_length(G, source = i, target = j))
                except:
                    factor = -1
                    return factor
        factor = sum(shortest_paths) / len(shortest_paths)
        factor = 1 / factor
        return factor
    else:
        factor = -1
        return factor


if __name__ == "__main__":
    main()