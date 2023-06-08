from bs4 import BeautifulSoup
import requests


archivo = open("Recetas_links.txt", "r")
errors_file=open("Bad_links.txt","w")

for linea in archivo.readlines():
    try:
        recipe_link=linea.strip()
        print(linea)
        html_recipe_info=requests.get(recipe_link).text

        soup_info_receta=BeautifulSoup(html_recipe_info,"lxml")
        
        recipe_name=soup_info_receta.find("h1", class_="comp type--lion article-heading mntl-text-block").text

        rating=soup_info_receta.find("div", id="mntl-recipe-review-bar__rating_1-0").text

        all_times_info=soup_info_receta.find_all("div",class_="mntl-recipe-details__item")

        for info in all_times_info:
            label = info.find("div",class_="mntl-recipe-details__label").text
            if label=="Total Time:":
                Total_time= info.find("div",class_="mntl-recipe-details__value").text
                break

        print(recipe_name.strip())
        print(rating)
        print(Total_time)
    
    except:
        errors_file.write(linea)
        continue