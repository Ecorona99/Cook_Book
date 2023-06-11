from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

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
    
    errors_file = open("Bad_links.txt", "w")

        # Crea una instancia del navegador
    driver = webdriver.Firefox()

    for line in f.readlines():
        
        recipe_link = line.strip()

        # Accede a la página
        driver.get(recipe_link)
        #Se espera para que se carguen todos los elemntos de la pagina
        #IMPORTANTE, depende de la velocidad de internet, pero aumentr mucho la espera demorara la ejecucion del 
        #programa
        driver.implicitly_wait(10)
        try:
            
            # Manejo de excepciones en caso de que no exista boton en una pagina
            try:
                
                boton = driver.find_element(By.CLASS_NAME,"feedback-list__load-more-button")
                
                # Si es posible se presiona el boton "count" veces
                count=2
                while (count>0):
                    boton.click()
                    # Espera a que se cargue el contenido
                    driver.implicitly_wait(20)
                    count-=1
                
            except NoSuchElementException:
                pass
            
            # Se carga el contenido del html
            html_recipe_info = driver.page_source
            #html_recipe_info = requests.get(recipe_link).text

            soup_recipe_info = BeautifulSoup(html_recipe_info, "lxml")
            
            recipe_name = soup_recipe_info.find("h1", class_ = "comp type--lion article-heading mntl-text-block").text

            rating = soup_recipe_info.find("div", id = "mntl-recipe-review-bar__rating_1-0").text
            
            # Tab que contiene la info de tiempos de preparacion
            all_times_info = soup_recipe_info.find_all("div", class_ = "mntl-recipe-details__item")
            
            # Solo es de interes el tiempo total de preparacion
            for info in all_times_info:
                label = info.find("div", class_ = "mntl-recipe-details__label").text
                if label== "Total Time:":
                    Total_time = info.find("div", class_ = "mntl-recipe-details__value").text
                    break
            
            ingredients_tags=soup_recipe_info.find_all("span", attrs={"data-ingredient-name":"true"} )
            
            ingredients_list=[x.text for x in ingredients_tags]
            
            print(recipe_name.strip())
            print(rating.strip())
            print(Total_time.strip())
            print(ingredients_list)

            feedback_list_tags=soup_recipe_info.find_all("div", class_="feedback__text")

            if len(feedback_list_tags)>0:

                feedback_list=[x.p.text for x in feedback_list_tags]
                
                # Se guardan los comentarios, separados por 2 lineas en blanco
                with open("Feedbacks.txt", "w") as f:
                    for comment in feedback_list:
                        f.write(f"{comment}\n\n")
                        print(comment+"\n\n")
              
        except:
            errors_file.write(line)
            continue

    driver.quit()

if __name__ == '__main__':
    main()

main()