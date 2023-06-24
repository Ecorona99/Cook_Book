import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re
from Graph_Crafting import score_recipe_ingredients

#* El set de datos no se subirá remotamente debido a su tamaño.
def main():
    #df_recipes = pd.read_parquet("recipes.parquet")
    #filter_recipes(df_recipes)
    
    #df_cleaned_recipes = pd.read_parquet("cleaned_recipes.parquet")
    #print(len(df_cleaned_recipes.index))

    #df_reviews = pd.read_parquet("reviews.parquet")
    #filter_reviews(df_cleaned_recipes, df_reviews)

    df_cleaned_reviews = pd.read_parquet("cleaned_reviews.parquet")
    sustitution_reviews(df_cleaned_reviews)
    #print(df_cleaned_reviews)
    pass

def filter_recipes(df_recipes):
    df = pd.DataFrame()
    df = df_recipes
    mask = df["RecipeIngredientParts"].apply(lambda x: len(x) == 0)
    df = df.drop(df[mask].index)
    selected_columns = ["RecipeId","Name","TotalTime","Description","RecipeCategory","Keywords",
                        "RecipeIngredientParts","AggregatedRating","ReviewCount","Calories",
                        "FatContent","SaturatedFatContent","CholesterolContent",
                        "SodiumContent","CarbohydrateContent","FiberContent","SugarContent",
                        "ProteinContent","RecipeServings","RecipeInstructions"]
    df = df[selected_columns]
    df = df.dropna(axis=0)
    df = df.reset_index(drop=True)
    df.to_parquet("cleaned_recipes.parquet")

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

def get_all_ingredients(df_recipes):
    all_ingredients = set()
    
    for n, recipe in df_recipes.iterrows():
        print(n)
        ingredients = get_ingredients(recipe)
        all_ingredients.update(ingredients)
    
    for i in all_ingredients:
        with open("ingredients.txt", "a") as f:
            f.write(i +"\n")
    print(len(all_ingredients))

def get_ingredients(recipe):
    ingredients = set()
    for ingredient in recipe["RecipeIngredientParts"]:
        ingredients.add(ingredient)
    ingredients = clean(ingredients)
    return ingredients

def get_recipe_by_ingredients(df_recipes, ingredients):
    ingredients = ingredients.split(",").strip
    ingredients = clean(ingredients)
    df_recipes["Match"] = df_recipes["RecipeIngredientParts"].apply(lambda x: score_recipe_ingredients(clean(x), ingredients))
    df_recipes = df_recipes.sort_values("Match", ascending = False)
    recipe = df_recipes.iloc[0]
    return recipe

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

def get_reviewers_id(recipe_id, df_reviews):
    df_reviews = df_reviews.loc[df_reviews["RecipeId"] == recipe_id]
    authorsId = set(df_reviews["AuthorId"])
    return authorsId

if __name__ == "__main__":
    main()