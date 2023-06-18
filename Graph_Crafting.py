import networkx as nx
import pandas as pd
from Data_Processing import get_ingredients

def main():
    create_ingredients_graph()

def create_ingredients_graph():
    df_recipes = pd.read_parquet("recipes.parquet")

    G = nx.Graph()

    for n, recipe in df_recipes.iterrows():
        ingredients_set = get_ingredients(recipe)
        ingredients = list(ingredients_set)
        for i in range(len(ingredients)-1):
            for j in range(i+1,len(ingredients)):
                if G.has_edge(ingredients[i],ingredients[j]):
                    peso = G.get_edge_data(ingredients[i],ingredients[j])["weight"]
                    G[ingredients[i]][ingredients[j]]["weight"] = peso + 1
                else:
                    G.add_edge(ingredients[i], ingredients[j], weight=1)

    nx.write_graphml(G, "Ingredients.graphml")

if __name__ == "__main__":
    main()