import networkx as nx
from networkx.algorithms.community import louvain_communities
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import NearestNeighbors
from Data_Processing import get_ingredients, get_reviewers_id
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
        
        closest_indices = indices[0][0:]
        return self.original_nutritional_df.iloc[closest_indices]

def main():
    clean_sustitutions_graph()
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


def create_sustitutions_graph():
    G = nx.read_graphml("Ingredients.graphml")
    sustitutions_graph = nx.Graph()
    df_sustitutions = pd.read_parquet("sustitutions.parquet")
    ingredients = []
    
    for node in G.nodes():
        ingredients.append(str(node))
    
    for _, review in df_sustitutions.iterrows():
        matches = []
        for i in ingredients:
            if i in review["Review"]:
                matches.append(i)
        if len(matches) > 1:
            for i in range(len(matches) - 1):
                for j in range(i+1, len(matches)):
                    if sustitutions_graph.has_edge(matches[i],matches[j]):
                        w = sustitutions_graph[matches[i]][matches[j]]['weight']
                        sustitutions_graph.add_edge(matches[i], matches[j], weight = w + 1)
                    else:
                        sustitutions_graph.add_edge(matches[i], matches[j], weight = 1)
    nx.write_graphml(sustitutions_graph, "Sustitutions.graphml")


def clean_sustitutions_graph():
    G = nx.read_graphml("Sustitutions.graphml")
    
    edges_to_remove = [(u, v) for u, v, d in G.edges(data = True) if d['weight'] < 5]
    G.remove_edges_from(edges_to_remove)

    isolated_nodes = [n for n in G.nodes() if G.degree(n) == 0]
    G.remove_nodes_from(isolated_nodes)
    
    communities = list(louvain_communities(G))
    for i,comm in enumerate(communities):
        for node in G.nodes():
            if node in comm:
                nx.set_node_attributes(G, {node: {'color': i}})
    nx.write_graphml(G, "Sustitutions_communities.graphml")


def calculate_ingredient_similarity(Ingredients_Graph, df_recipes, recipe_id):
    recipe = df_recipes.loc[df_recipes['RecipeId'] == recipe_id].iloc[0]

    df_recipes["factor"] = df_recipes.apply(lambda x: shortest_path_factor(Ingredients_Graph, recipe, x), axis = 1)
    recipe_factor_max = df_recipes.sort_values("factor", ascending = False)
    return recipe_factor_max.iloc[1:10], recipe_id


def calculate_nutritional_similarity(df_recipes, recipe_id):
    nutritional_columns = ["RecipeId", "Name", "Calories", "FatContent", "SaturatedFatContent", "CholesterolContent", 
                           "SodiumContent", "CarbohydrateContent","FiberContent", "SugarContent", "ProteinContent", 
                           "RecipeServings"]
    nutritional_df = df_recipes[nutritional_columns]
    nutritional_data_columns = ["Calories", "FatContent", "SaturatedFatContent", "CholesterolContent", "SodiumContent",
                      "CarbohydrateContent", "FiberContent", "SugarContent", "ProteinContent"]
    nutritional_df.loc[:,nutritional_data_columns] = nutritional_df.loc[:,nutritional_data_columns].div(nutritional_df["RecipeServings"], axis=0)
    nutritional_df.drop("RecipeServings", axis=1)
    recommender = NutritionalRecommender(nutritional_df, nutritional_data_columns)
    nutritional_sim_df = recommender.find_closest_recipes(recipe_id, k = 500)
    df_recipes = pd.merge(nutritional_sim_df[["RecipeId"]], df_recipes, on = "RecipeId", how = "inner")
    return df_recipes, recipe_id


def calculate_reviewers_similarity(Reviewers_Graph, df_recipes, recipe_id):
    df = pd.DataFrame()

    recipe = df_recipes.loc[df_recipes['RecipeId'] == recipe_id].iloc[0]
    neighbors = Reviewers_Graph.neighbors(recipe["Name"])
    for neighbor in neighbors:
        fila = df_recipes.loc[df_recipes["Name"] == str(neighbor)].iloc[0]
        fila_df = fila.to_frame().T
        df = pd.concat([df, fila_df], ignore_index=True)
    return df, recipe_id


def calculate_PMI(Recipe_Graph, A_ingredient, B_ingredient, total):
    Pa = len(list(Recipe_Graph.predecessors(A_ingredient))) / total
    Pb = len(list(Recipe_Graph.predecessors(B_ingredient))) / total
    Pab = len(set(Recipe_Graph.predecessors(A_ingredient)) & set(Recipe_Graph.predecessors(B_ingredient))) / total
    PMI = log(Pab/(Pa*Pb))
    return PMI


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


if __name__ == "__main__":
    main()