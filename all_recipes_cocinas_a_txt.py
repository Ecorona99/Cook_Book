from bs4 import BeautifulSoup 
import requests 
import time


# pagina donde aparecen las diferentes cocinas por regiones, organizadas alfabeticamente
html_cocinas_paises=requests.get("https://www.allrecipes.com/cuisine-a-z-6740455").text

soup_cocinas_paises=BeautifulSoup(html_cocinas_paises,"lxml")

# esta clase es la que contiene cada region en particular, por lo tanto busco todas las clases de la pagina
cocinas=soup_cocinas_paises.find_all("li", class_="comp link-list__item")

href="href"

with open("Cocinas_info.txt","w") as f:
    for cocina in cocinas:
        # guardo el nombre de la region  
        f.write(cocina.a.text + "\nRecipes: \n")
        # accedo al link de la region, se carga la pagina que contiene todas las recetas de dicha region
        html_recetas=requests.get(cocina.a[href]).text
        
        soup_recetas=BeautifulSoup(html_recetas,"lxml")
        # clase que contiene cada receta en particular, busco todas las clases de la pagina
        recetas=soup_recetas.find_all("a", class_="comp mntl-card-list-items mntl-document-card mntl-card card card--no-image")
        

        for receta in recetas:

            # clase que contiene el nombre y link a la info de cada receta en particular 
            recipe_card=receta.find("div", class_="card__content")
            # nobre de la receta
            recipe_name=recipe_card.span.span.text
            # link de la receta
            recipe_link=receta[href]
            # pagina de la receta
            html_recipe_info=requests.get(recipe_link).text
                
            f.write(recipe_name + "\nLink: "+ recipe_link  )
            f.write("\n\n\n")

            


        
              
          
