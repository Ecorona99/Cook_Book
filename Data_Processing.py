import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re

#* El set de datos no se subirá remotamente debido a su tamaño.
def main():
    pass

def filter_recipes(df_recipes):
    mask = df_recipes["RecipeIngredientParts"].apply(lambda x: len(x) == 0)
    df_recipes = df_recipes.drop(df_recipes[mask].index)
    selected_columns = ["RecipeId","Name","TotalTime","Description","RecipeCategory","Keywords",
                        "RecipeIngredientParts","AggregatedRating","ReviewCount","Calories",
                        "FatContent","SaturatedFatContent","CholesterolContent",
                        "SodiumContent","CarbohydrateContent","FiberContent","SugarContent",
                        "ProteinContent","RecipeServings","RecipeInstructions"]
    df_recipes = df_recipes[selected_columns]
    df_recipes = df_recipes.dropna(axis=0)
    df_recipes = df_recipes.reset_index(drop=True)
    df_recipes.to_parquet("cleaned_recipes.parquet")

def filter_reviews(df_recipes, df_reviews):
    df_reviews_filtrado = pd.merge(df_recipes[["RecipeId"]], df_reviews, on = "RecipeId", how = "inner")
    df_reviews_filtrado = df_reviews_filtrado.reset_index(drop = True)
    columns = ["RecipeId", "ReviewId", "AuthorId", "AuthorName", "Rating", "Review"]
    df_reviews_filtrado = df_reviews_filtrado[columns]
    df_reviews_filtrado.to_parquet("cleaned_reviews.parquet")

def sustitution_reviews(df_reviews):
    df_reviews["Found"] = df_reviews["Review"].apply(lambda x: re.search(r"(.+\b(replace|change|substitute|swap)((\s+\b\w+\b){0,5})\s+(\bwith\b|\bfor\b|\binstead\b)((\s+\b\w+\b){0,5})\b)", x) != None)
    df_reviews = df_reviews.loc[df_reviews["Found"] == True]
    df_reviews.to_parquet("sustitutions.parquet")

def get_recipe_id(df_recipes, recipe_name):
    id_receta = df_recipes.loc[df_recipes["Name"] == recipe_name, "RecipeId"].values[0]
    return id_receta

def get_ingredients(recipe):
    ingredients = set()
    for ingredient in recipe["RecipeIngredientParts"]:
        ingredients.add(ingredient)
    ingredients = clean(ingredients)
    return ingredients

def clean(ingredients):
    tokenized = [nltk.word_tokenize(i.lower()) for i in ingredients]

    stop_words = set(stopwords.words("english"))
    stop_words.update(['.', ',', '"', "'", '?', '!', ':', ';', '(', ')', '[', ']', '{', '}'])
    non_stop_tokens = [[w for w in i if not w in stop_words] for i in tokenized]

    lemmatizer = WordNetLemmatizer()
    lemmatizeds = [[lemmatizer.lemmatize(w) for w in i] for i in non_stop_tokens]

    cleaned_ingredients = set()
    for trated_ingredients in lemmatizeds:
        trated_ingredients = " ".join(trated_ingredients)
        cleaned_ingredients.add(trated_ingredients)
    return cleaned_ingredients

def calculate_PMI_neighbors(Ingredients_Graph, df_recipes, recipe_id):
    PMI_ingredients = set()
    n = 4999
    
    recipe = df_recipes.loc[df_recipes['RecipeId'] == recipe_id].iloc[0]
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
    df_recipes_PMI = df_recipes.sort_values("Coincidences", ascending = False)
    df_recipes_PMI = df_recipes_PMI.iloc[0:n]
    return df_recipes_PMI, recipe_id

def score_recipe_ingredients(recipe_ingredients, ingredients) -> int:
    score = 0
    for i in ingredients:
        if i in recipe_ingredients:
            score += 1
    return int(score)

def get_recipe_by_ingredients_using_graph(Recipes_Graph, ingredients):
    ingredients = ingredients.split(",")
    ingredients = clean(ingredients)
    first_run = 1
    for ingredient in ingredients:
        recetas = set(Recipes_Graph.predecessors(ingredient))
        if first_run == 1:
            result = recetas
            first_run = 0
        else:
            result = result & recetas
    return list(result)

def get_reviewers_id(recipe_id, df_reviews):
    df_reviews = df_reviews.loc[df_reviews["RecipeId"] == recipe_id]
    authorsId = set(df_reviews["AuthorId"])
    return authorsId

if __name__ == "__main__":
    main()