import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

#* El set de datos no se subirá remotamente debido a su tamaño
def main():
    df = pd.read_parquet("recipes.parquet")

    # esquema = df.dtypes
    # print(esquema)

    for n, recipe in df.iterrows():
        ingredients = get_ingredients(recipe)
        print(ingredients)
        if n == 10:
            break
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