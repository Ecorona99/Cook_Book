from bs4 import BeautifulSoup
import requests
import time


# pagina donde aparecen los diferentes tipos de recetas, organizadas alfabeticamente
html_recetas_a_z=requests.get("https://www.allrecipes.com/recipes-a-z-6735880").text

soup_tipos_recetas=BeautifulSoup(html_recetas_a_z,"lxml")

# esta clase es la que contiene cada tipo en particular
tipo_receta=soup_tipos_recetas.find_all("li", class_="comp link-list__item")

link_set=set()


with open("Recetas_links.txt","w") as f:
    for elemento in tipo_receta:
        # accedo al link del tipo de cocina en particular
        link_tipo_receta=elemento.a["href"]

        html_recetas=requests.get(link_tipo_receta).text
        
        soup_recetas=BeautifulSoup(html_recetas,"lxml")

        # clase que contiene cada receta en particular, busco todas las clases de la pagina
        recetas=soup_recetas.find_all("a", class_="comp mntl-card-list-items mntl-document-card mntl-card card card--no-image")
        
        for receta in recetas:
            # link de la receta
            recipe_link=receta["href"]

            link_set.add(recipe_link)
           
        
    for link in link_set:

        f.write(f"{link}\n")
            



           


            


        
              
          
