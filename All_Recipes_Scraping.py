from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.common.exceptions import (NoSuchElementException,TimeoutException)
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.support.wait import WebDriverWait


def main():
    
    #allrecipes_to_txt()
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
    
    f = open("Recetas_links.txt", "r")

    # Crea una instancia del navegador por defecto.
    driver = webdriver.Firefox()
    time.sleep(1)

    count = 0

    for line in f.readlines():

        count += 1
        if count == 5:
            break

        recipe_link = line.strip()

        # Accede a la página.
        driver.get(recipe_link)

        # Manejo de excepciones imprevistas quedarán anotadas las recetas que las provoquen en un txt.
        try: 
            
            # Manejo de excepciones en caso de que no exista botón de más comentarios en una página.
            try:
                
                #Si es posible se presiona el botón determinadas veces.
                for i in range(2):
                    #Se espera a que cargue el boton, o un max de 20s
                    button = WebDriverWait(driver, timeout=20).until(lambda d: d.find_element(By.CLASS_NAME,"feedback-list__load-more-button")) 
                    button.click()    

            except TimeoutException :
                pass
                        
            # Se carga el contenido del html
            html_recipe_info = driver.page_source

            soup_recipe_info = BeautifulSoup(html_recipe_info, "lxml")
            
            recipe_name = soup_recipe_info.find("h1", class_ = "comp type--lion article-heading mntl-text-block").text

            try:
                rating = soup_recipe_info.find("div", id = "mntl-recipe-review-bar__rating_1-0").text
            except:
                rating = "0.0"

            # Tab que contiene la info de tiempos de preparación.
            all_times_info = soup_recipe_info.find_all("div", class_ = "mntl-recipe-details__item")
            
            # Solo es de interés el tiempo total de preparación.
            for info in all_times_info:
                label = info.find("div", class_ = "mntl-recipe-details__label").text
                if label == "Total Time:":
                    total_time = info.find("div", class_ = "mntl-recipe-details__value").text
                    break            
            
            ingredients_tags = soup_recipe_info.find_all("span", attrs = {"data-ingredient-name": "true"})
            
            ingredients_list = [x.text for x in ingredients_tags]
            
            with open("Ingredients.txt", "a") as f_ing:
                for ingredient in ingredients_list:
                    f_ing.write(ingredient)
                    f_ing.write("\n")

            nutrition_facts = {}

            table_nutrition = soup_recipe_info.find_all("tr", class_ = "mntl-nutrition-facts-summary__table-row")
            for row in table_nutrition:
                try:
                    key = row.find("td", class_ = "mntl-nutrition-facts-summary__table-cell type--dogg").text
                except:
                    key = row.find("td", class_ = "mntl-nutrition-facts-summary__table-cell type--dog").text
                    
                value = row.find("td", class_ = "mntl-nutrition-facts-summary__table-cell type--dog-bold").text
                nutrition_facts.update({key:value})

            # Se espera a que carguen los comentarios
            WebDriverWait(driver, timeout=5).until(lambda d: d.find_element(By.CLASS_NAME,"feedback__text"))
            feedback_list_tags = soup_recipe_info.find_all("div", class_ = "feedback__text")

            if len(feedback_list_tags) > 0:

                feedback_list = [x.p.text for x in feedback_list_tags]

                # Se guardan los comentarios, separados por 2 lineas en blanco.
                with open("Feedbacks.txt", "w") as f_feed:
                    for comment in feedback_list:
                        f_feed.write(f"{comment}\n\n")
                        print(comment + "\n\n")  
            
            print(recipe_name.strip())
            print(rating.strip())
            print(total_time.strip())
            print(ingredients_list)

        except :
            with open("Bad_links.txt", "w") as errors:
                errors.write(recipe_link + "\n")
            continue

    f.close()
    driver.quit()

if __name__ == "__main__":
    main()
