from bs4 import BeautifulSoup
import requests

def main():
    allrecipes_to_txt()
    recipes_info()

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

def recipes_info():
    
    file = open("Recetas_links.txt", "r")
    
    errors_file = open("Bad_links.txt", "w")

    for line in file.readlines():
        try:
            recipe_link = line.strip()

            html_recipe_info = requests.get(recipe_link).text

            soup_recipe_info = BeautifulSoup(html_recipe_info, "lxml")
            
            recipe_name = soup_recipe_info.find("h1", class_ = "comp type--lion article-heading mntl-text-block").text

            rating = soup_recipe_info.find("div", id = "mntl-recipe-review-bar__rating_1-0").text

            all_times_info = soup_recipe_info.find_all("div", class_ = "mntl-recipe-details__item")

            for info in all_times_info:
                label = info.find("div", class_ = "mntl-recipe-details__label").text
                if label== "Total Time:":
                    Total_time = info.find("div", class_ = "mntl-recipe-details__value").text
                    break

            print(recipe_name.strip())
            print(rating)
            print(Total_time)
        
        except:
            errors_file.write(line)
            continue

if __name__ == '__main__':
    main()
