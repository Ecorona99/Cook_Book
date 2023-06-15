import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re

#* El set de datos no se subirá remotamente debido a su tamaño
def main():
    df_recipes = pd.read_parquet("recipes.parquet")
    #df_reviews = pd.read_parquet("reviews.parquet")

    # esquema = df_recipes.dtypes
    # print(esquema)
    all_ingredients = set()
    for n, recipe in df_recipes.iterrows():
        ingredients = get_ingredients(recipe)
        all_ingredients.update(ingredients)
    print(all_ingredients)
    print(len(all_ingredients))
    print("")


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