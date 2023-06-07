from bs4 import BeautifulSoup
import requests
import time


# Página donde aparecen las diferentes cocinas por regiones, organizadas alfabéticamente.
html_cocinas_paises = requests.get("https://www.allrecipes.com/cuisine-a-z-6740455").text

soup_cocinas_paises = BeautifulSoup(html_cocinas_paises, "lxml")

# Esta clase es la que contiene cada región en particular, por lo tanto busco todas las clases de la página.
cocinas=soup_cocinas_paises.find_all("li", class_ = "comp link-list__item")

with open("Cocinas_info.txt", "w") as f:
    for cocina in cocinas:
        
        # Guardo el nombre de la región.
        f.write(cocina.a.text + "\nRecipes: \n")
        # Accedo al link de la región, se carga la página que contiene todas las recetas de dicha región.
        html_recetas = requests.get(cocina.a["href"]).text
        
        soup_recetas = BeautifulSoup(html_recetas, "lxml")
        # clase que contiene cada receta en particular, busco todas las clases de la página.
        recetas = soup_recetas.find_all("a", class_ = "comp mntl-card-list-items mntl-document-card mntl-card card card--no-image")
        
        for receta in recetas:

            # Clase que contiene el nombre y link a la info de cada receta en particular.
            recipe_card = receta.find("div", class_="card__content")
            # Nombre de la receta.
            recipe_name = recipe_card.span.span.text
            # Link de la receta.
            recipe_link = receta["href"]
            # Página de la receta.
            html_recipe_info = requests.get(recipe_link).text
                
            f.write(recipe_name + "\nLink: "+ recipe_link  )
            f.write("\n\n\n")
