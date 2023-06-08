from bs4 import BeautifulSoup
import requests

def main():
    allrecipes_to_txt()

def allrecipes_to_txt():
    # Página donde aparecen los diferentes tipos de recetas, organizadas alfabéticamente.
    html_allrecipes = requests.get("https://www.allrecipes.com/recipes-a-z-6735880").text

    soup_allrecipes = BeautifulSoup(html_allrecipes, "lxml")

    # Clase que contiene cada instancia de un tipo de receta, se buscan todas las clases de la página.
    recipe_types = soup_allrecipes.find_all("li", class_ = "comp link-list__item")

    link_set = set()

    for recipe_type in recipe_types:
        # Accedo al link del tipo de cocina en particular.
        recipe_type_link = recipe_type.a["href"]

        html_recipe_type = requests.get(recipe_type_link).text
        
        soup_recipe_type = BeautifulSoup(html_recipe_type, "lxml")
        
        # Clase que contiene cada instancia de una receta, se buscan todas las clases de la página.
        recipes = soup_recipe_type.find_all("a", class_ = "comp mntl-card-list-items mntl-document-card mntl-card card card--no-image")
        
        for recipe in recipes:
            # Link de la receta.
            recipe_link = recipe["href"]
        
            link_set.add(recipe_link)
                
    with open("Recetas_links.txt", "w") as f:
        for link in link_set:
            f.write(f"{link}\n")


if __name__ == '__main__':
    main()
