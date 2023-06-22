import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re

#* El set de datos no se subirá remotamente debido a su tamaño.
def main():
    df_recipes = pd.read_parquet("recipes.parquet")
    print(len(df_recipes.index))
    #filter_recipes(df_recipes)
    
    df_cleaned_recipes = pd.read_parquet("cleaned_recipes.parquet")
    print(len(df_cleaned_recipes.index))
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

def sustitution_reviews(df_reviews):
    df = pd.DataFrame()
    for n, review in df_reviews.iterrows():
        reemplazo = re.search(r"(.+\b(replace|change|substitute|swap)((\s+\b\w+\b){0,5})\s+(\bwith\b|\bfor\b|\binstead\b)((\s+\b\w+\b){0,5})\b)",review["Review"])
        if reemplazo:
            fila = df_reviews.iloc[n]
            fila_df = fila.to_frame().T
            df = pd.concat([df, fila_df], ignore_index=True)
    df.to_parquet("sustitutions.parquet")

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

if __name__ == "__main__":
    main()