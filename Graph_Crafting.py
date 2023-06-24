import networkx as nx
from networkx.algorithms.community.label_propagation import label_propagation_communities
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import NearestNeighbors
from Data_Processing import get_ingredients
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

    def find_closest_recipes(self, recipe_id, k=10):
        input_recipe = self.nutritional_df.loc[self.nutritional_df["RecipeId"] == recipe_id, self.nutritional_data_columns]
        distances, indices = self.knn.kneighbors(input_recipe, n_neighbors=k+1)
        
        closest_indices = indices[0][1:]
        return self.original_nutritional_df.iloc[closest_indices]

def main():
    #create_recipe_graph()
    #create_ingredients_graph()

    #df_recipes, recipe = calculate_PMI_neighbors(164136.0)
    #calculate_ingredient_similarity(df_recipes, recipe)
    #calculate_nutritional_similarity()

    recipe_with_high_reviews()
    pass


def create_recipe_graph():
    df_recipes = pd.read_parquet("cleaned_recipes.parquet")

    G = nx.DiGraph()
    for n, recipe in df_recipes.iterrows():
        ingredients_set = get_ingredients(recipe)
        ingredients = list(ingredients_set)
        for i in range(len(ingredients)):
            G.add_edge(recipe["Name"], ingredients[i])
    nx.write_graphml(G, "Recipes.graphml")


def create_ingredients_graph():
    df_recipes = pd.read_parquet("cleaned_recipes.parquet")
    Recipe_Graph = nx.read_graphml("Recipes.graphml")
    G = nx.Graph()
    total_recetas = len(df_recipes.index)
    for n, recipe in df_recipes.iterrows():
        ingredients_set = get_ingredients(recipe)
        ingredients = list(ingredients_set)
        for i in range(len(ingredients)-1):
            for j in range(i+1,len(ingredients)):
                if G.has_edge(ingredients[i],ingredients[j]):
                    pass    
                else:
                    PMI = calculate_PMI(Recipe_Graph, ingredients[i], ingredients[j], total_recetas)
                    G.add_edge(ingredients[i], ingredients[j], weight = PMI)
    nx.write_graphml(G, "Ingredients.graphml")


def calculate_ingredient_similarity(df_recipes, recipe):
    Ingredients_Graph = nx.read_graphml("Ingredients.graphml")

    receta_indicada = recipe
    df_recipes["factor"] = df_recipes.apply(lambda x: shortest_path_factor(Ingredients_Graph, receta_indicada, x), axis = 1)
    print(df_recipes["factor"])
    recipe_factor_max = df_recipes.sort_values("factor", ascending = False)
    print(recipe_factor_max[0:9])


def calculate_PMI_neighbors(recipe_id):
    df_recipes = pd.read_parquet("cleaned_recipes.parquet")
    Ingredients_Graph = nx.read_graphml("Ingredients.graphml")
    PMI_ingredients = set()

    index = df_recipes.index[df_recipes['RecipeId'] == recipe_id]
    recipe = df_recipes.iloc[index.argmax()]
    print(index)
    print(recipe)
    ingredients = get_ingredients(recipe)
    
    for i in ingredients:
        neighbors = Ingredients_Graph.neighbors(i)
        PMI_ingredients.add(i)

        max_PMI_neighbor = None
        max_weight = 0
        for neighbor in neighbors:
            weight = Ingredients_Graph[i][neighbor]['weight']
            if weight > max_weight:
                max_PMI_neighbor = neighbor
                max_weight = weight
                PMI_ingredients.add(max_PMI_neighbor)
    
    df_recipes["Coincidences"] = df_recipes["RecipeIngredientParts"].apply(lambda x: score_recipe_ingredients(x, PMI_ingredients))
    df_recipes = df_recipes.sort_values("Coincidences", ascending = False)
    print(df_recipes.dtypes)
    df_recipes = df_recipes.iloc[0:49]
    return df_recipes, recipe


def calculate_nutritional_similarity():
    df_recipes = pd.read_parquet("cleaned_recipes.parquet")
    nutritional_columns = ["RecipeId", "Name", "Calories", "FatContent", "SaturatedFatContent", "CholesterolContent", 
                           "SodiumContent", "CarbohydrateContent","FiberContent", "SugarContent", "ProteinContent", 
                           "RecipeServings"]
    nutritional_df = df_recipes[nutritional_columns]
    nutritional_data_columns = ["Calories", "FatContent", "SaturatedFatContent", "CholesterolContent", "SodiumContent",
                      "CarbohydrateContent", "FiberContent", "SugarContent", "ProteinContent"]
    nutritional_df.loc[:,nutritional_data_columns] = nutritional_df.loc[:,nutritional_data_columns].div(nutritional_df["RecipeServings"], axis=0)
    nutritional_df.drop("RecipeServings", axis=1)
    recommender = NutritionalRecommender(nutritional_df, nutritional_data_columns)
    input_recipe_id = 38.0
    result = recommender.find_closest_recipes(input_recipe_id)
    print(result)


def calculate_PMI(Recipe_Graph, A_ingredient, B_ingredient, total):
    Pa = len(list(Recipe_Graph.predecessors(A_ingredient))) / total
    Pb = len(list(Recipe_Graph.predecessors(B_ingredient))) / total
    Pab = len(set(Recipe_Graph.predecessors(A_ingredient)) & set(Recipe_Graph.predecessors(B_ingredient))) / total
    PMI = log(Pab/(Pa*Pb))
    return PMI


def score_recipe_ingredients(recipe_ingredients, ingredients) -> int:
    score = 0
    for i in ingredients:
        if i in recipe_ingredients:
            score += 1
    return int(score)


def shortest_path_factor(G, A_Recipe, B_Recipe) -> float:
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


def recipe_with_high_reviews():
    df_recipes_all = pd.read_parquet("cleaned_recipes.parquet")
    df_reviews = pd.read_parquet("cleaned_reviews.parquet")
    G = nx.Graph()

    df_recipes_all = df_recipes_all[df_recipes_all["ReviewCount"] > 10]
    df_recipes_all["Reviewers"] = df_recipes_all["RecipeId"].apply(lambda x: reviewers_id(x, df_reviews))
    print(df_recipes_all["Reviewers"])
    for n, recipe in df_recipes_all.iterrows():
        df_recipes = df_recipes_all.copy()
        df_recipes["AuthorsMatch"] = df_recipes["Reviewers"].apply(lambda x: len(x.intersection(recipe["Reviewers"])) > 5)
        df_recipes = df_recipes.loc[df_recipes["AuthorsMatch"] == True]
        for m, match in df_recipes.iterrows():
            if recipe["RecipeId"] != match["RecipeId"]:
                G.add_edge(recipe["Name"], match["Name"])
        if n > 1000:
            break
    nx.write_graphml(G, "Costumers.graphml")
    
    
def reviewers_id(recipe_id, df_reviews):
    df_reviews = df_reviews.loc[df_reviews["RecipeId"] == recipe_id]
    authorsId = set(df_reviews["AuthorId"])
    return authorsId

if __name__ == "__main__":
    main()