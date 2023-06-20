import networkx as nx
import pandas as pd
from Data_Processing import get_ingredients
from math import log

def main():
    create_ingredients_graph()
    #df_recipes = pd.read_parquet("recipes.parquet")
    #create_recipe_graph()
    pass

def create_ingredients_graph():
    df_recipes = pd.read_parquet("recipes.parquet")
    Recipe_Graph = nx.read_graphml("Recipes.graphml")
    G = nx.Graph()
    #total_recetas = len(df_recipes.index)
    total_recetas = 1000
    for n, recipe in df_recipes.iterrows():
        ingredients_set = get_ingredients(recipe)
        ingredients = list(ingredients_set)
        for i in range(len(ingredients)-1):
            for j in range(i+1,len(ingredients)):
                if G.has_edge(ingredients[i],ingredients[j]):
                    pass    
                else:
                    PMI = calculate_PMI(Recipe_Graph, ingredients[i], ingredients[j], total_recetas)
                    if PMI > 0:
                        G.add_edge(ingredients[i], ingredients[j], weight = PMI)
        if n > 1000:
            break
    nx.write_graphml(G, "Ingredients.graphml")

def create_recipe_graph():
    df_recipes = pd.read_parquet("recipes.parquet")

    G = nx.DiGraph()
    for n, recipe in df_recipes.iterrows():
        ingredients_set = get_ingredients(recipe)
        ingredients = list(ingredients_set)
        for i in range(len(ingredients)):
            G.add_edge(recipe["Name"], ingredients[i])
        if n > 1000:
            break
    nx.write_graphml(G, "Recipes.graphml")

def calculate_PMI(Recipe_Graph, A_ingredient, B_ingredient,total):
    Pa = len(list(Recipe_Graph.predecessors(A_ingredient))) / total
    Pb = len(list(Recipe_Graph.predecessors(B_ingredient))) / total
    Pab = len(set(Recipe_Graph.predecessors(A_ingredient)) & set(Recipe_Graph.predecessors(B_ingredient))) / total
    PMI = log(Pab/(Pa*Pb))
    return PMI

if __name__ == "__main__":
    main()