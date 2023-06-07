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

            # clase que contiene el nombre y link a la info de cada receta en particular 
            recipe_card=receta.find("div", class_="card__content")
            # nobre de la receta
            recipe_name=recipe_card.span.span.text
            # link de la receta
            recipe_link=receta["href"]

            link_set.add(recipe_link)
           
        
    for link in link_set:

        f.write(f"{link}\n")
            



            ### De aca para abajo se empieza a extraer info de cada receta ###


            # pagina de la receta

            #html_recipe_info=requests.get(recipe_link).text

            #soup_info_receta=BeautifulSoup(html_recipe_info,"lxml")

            #rating=soup_info_receta.find("div", id="mntl-recipe-review-bar__rating_1-0")

            #all_times_info=soup_info_receta.find_all("div",class_="mntl-recipe-details__item")

            #for info in all_times_info:
            #    label = info.find("div",class_="mntl-recipe-details__label").text
            #    if label=="Total Time:":
            #        Total_time= info.find("div",class_="mntl-recipe-details__value").text
            #        break


            


        
              
          
