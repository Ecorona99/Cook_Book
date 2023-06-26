import tkinter as tk
import ttkbootstrap as ttk
import pandas as pd
import networkx as nx
import re
from Data_Processing import get_recipe_id, calculate_PMI_neighbors, get_recipe_by_ingredients_using_graph, get_ingredients
from networkx import NetworkXError
from Graph_Crafting import calculate_reviewers_similarity,calculate_nutritional_similarity,calculate_ingredient_similarity

df_recipes = pd.read_parquet("cleaned_recipes.parquet")
Ingredients_Graph = nx.read_graphml("Ingredients.graphml")
Reviewers_Graph = nx.read_graphml("Reviewers.graphml")
Recipes_Graph = nx.read_graphml("Recipes.graphml")
#####################################################################################################################

def filtro(df_recipes, recipe_name, filter_output_frame, check_box_filtro_pmi_status, check_box_filtro_nutricional_status, check_box_filtro_reviews_status):
    try:
        recipe_id = get_recipe_id(df_recipes, recipe_name)
        print(check_box_filtro_pmi_status, check_box_filtro_nutricional_status, check_box_filtro_reviews_status)
        if check_box_filtro_pmi_status.get() == 1:
            df_recipes, recipe_id = calculate_PMI_neighbors(Ingredients_Graph, df_recipes, recipe_id)
        if  check_box_filtro_reviews_status.get() == 1:
            df_recipes, recipe_id = calculate_reviewers_similarity(Reviewers_Graph, df_recipes, recipe_id)
        if check_box_filtro_nutricional_status.get() == 1 :
            df_recipes,recipe_id = calculate_nutritional_similarity(df_recipes, recipe_id)
        df_recipes, recipe_id = calculate_ingredient_similarity(Ingredients_Graph, df_recipes, recipe_id)

        sugerencias_var = ttk.StringVar(value = df_recipes["Name"].to_list())
        sugerencias_label = ttk.Label(filter_output_frame, text = "Te podrian gustar:", font = "Calibri 12").pack()
        sugerencias_list = tk.Listbox(filter_output_frame, height = 10, width = 30, listvariable = sugerencias_var, font = "Calibri 12").pack()
    except:
        output_label = ttk.Label(filter_output_frame, text = "No se encontraron coincidencias", font = "Calibri 18 bold")
        filter_output_frame.place(relx = 0.5, rely = 0.5, anchor = tk.CENTER, relwidth = 0.8, relheight = 0.4)
        output_label.pack(fill = "x")

######################################################################################################################

def close_current_tab():
    current_tab = notebook.select()
    if current_tab:
        notebook.forget(notebook.index(current_tab))

def search():
    button_status.set("Searching...")
    window.update()

    # Frame de resultados de búsqueda
    output_window = ttk.Frame(notebook)
    output_frame = ttk.Frame(output_window)
    close_tab = ttk.Button(output_frame, text = "Close", command = close_current_tab)

    if check_box_state.get() == 1:
        try:
            notebook.add(output_window, text = "Resultados de busqueda", sticky = "nsew")
            output_label = ttk.Label(output_frame, text="Mejores coincidencias por ingredientes: ", font = "Calibri 18 bold")
            results = get_recipe_by_ingredients_using_graph(Recipes_Graph, input_recipe.get())
            list_var = ttk.StringVar(value = results)
            results_list = tk.Listbox(output_frame, height = 20, width = 70, listvariable = list_var)
            results_list.bind("<<ListboxSelect>>", my_click_on_search_results)
            output_frame.pack(expand = True, fill = "both")
            output_label.place(relx = 0.5, rely = 0.1, anchor = tk.CENTER)
            results_list.place(relx=0.5, rely = 0.5, anchor = tk.CENTER)
            close_tab.pack(pady = 5, side = "bottom")
            
        except NetworkXError:
            notebook.add(output_window, text = "Resultados de busqueda", sticky = "nsew")
            output_label = ttk.Label(output_frame, text="Parece que no encontramos coincidencias,\n prueba otras combinaciones de ingredientes,\n o asegurate dehaber escrito correctamente los nombres.", font = "Calibri 18 bold")
            output_frame.place(relx = 0.5, rely = 0.5, anchor = tk.CENTER, relwidth = 0.8, relheight = 0.4)
            output_label.pack(fill = "x")
            close_tab.pack(pady = 5, side = "bottom")
    else:
        value=input_recipe.get() 
        recipe = df_recipes.loc[df_recipes["Name"] == value].iloc[0]
        add_info_tab(recipe)
    button_status.set("Search")
    window.update()

##########################################################################################################

def check_box_toggle():
    if check_box_state.get() == 1:
        input_label_text.set("Buscar recetas por sus ingredientes:")
        coincidences_frame.pack_forget()
    else:
        input_label_text.set("Buscar receta por nombre:")
        coincidences_frame.pack(pady = 10, side = "bottom")
       
##################################################################################################################### 
        
# Main window
window = tk.Tk()
window.title("Cook-book V1.0")
window.geometry("800x600")
window.resizable(0,0)
window.update_idletasks()
notebook = ttk.Notebook(window)
notebook.pack(fill = "both", expand = True)
main_tab = ttk.Frame(notebook)
notebook.add(main_tab, text = "Buscar")
window_height = window.winfo_height()
window_width = window.winfo_width()

"""
# Background
photo = Image.open("sources/background.jpg")
backgroung_image = ImageTk.PhotoImage(photo)
background_label = ttk.Label(window, image = backgroung_image)
background_label.place(x = 0, y = 0)
background_label.lower()
"""

# Input Frame
input_frame = ttk.Frame(main_tab)
input_label_text = ttk.StringVar(value = "Buscar receta por nombre:")
input_label = ttk.Label(input_frame, width = 30, text = "Receta a buscar:", font = "Calibri 18 bold", anchor = tk.CENTER, textvariable = input_label_text)
input_recipe = ttk.StringVar()
search_field = ttk.Entry(input_frame, textvariable = input_recipe)
button_status = ttk.StringVar()
button_status.set("Search")
search_button = ttk.Button(input_frame, textvariable = button_status, command = search)
# Check box frame
check_box_frame = ttk.Frame(main_tab)
check_box_label = ttk.Label(check_box_frame, text = "Buscar por ingredientes", font = "Calibri 10")
check_box_state = ttk.IntVar()
check_box = ttk.Checkbutton(check_box_frame, command = check_box_toggle, variable = check_box_state)
# Coincidences frame
coincidences_frame = ttk.Frame(main_tab, name = "coincidences_frame")

# Packing elements to main window frames
input_frame.place(x = window_width // 2, y = window_height // 5, anchor = tk.CENTER)
input_label.pack(pady = 5)
search_field.pack(pady = 10, side = "left", expand = True, fill = "x")
search_button.pack(pady = 10, side = "right")
window.update_idletasks()
check_box_frame.place(x = window_width // 2, y=input_frame.winfo_height() + input_frame.winfo_y() + 25, anchor = tk.CENTER)
check_box_label.pack(pady = 5)
check_box.pack(pady = 5)
window.update()



list = tk.Listbox(coincidences_frame, height = 15, width = 50 , font = "Calibri 10 bold", relief = 'flat',
                  bg = "SystemButtonFace" , highlightcolor = "SystemButtonFace")



def my_click_on_search_results(my_widget):
    window = my_widget.widget
    index = int(window.curselection()[0])
    value = window.get(index)
    recipe = df_recipes.loc[df_recipes["Name"] == value].iloc[0]
    add_info_tab(recipe)


def add_info_tab(recipe):
    info_tab = ttk.Frame(notebook) 
    info_frame = ttk.Frame(info_tab)
    filter_output_frame=ttk.Frame(info_tab)
    filter_menu_frame=ttk.Frame(info_tab)
    close_button_frame=ttk.Frame(info_tab)

    name = recipe["Name"]
    ### Info frame ##############################################
    notebook.add(info_tab, text=name)
    info_frame.place(x=0, y=0, relwidth=0.6, relheight=0.9)
    filter_menu_frame.place(relx=0.6, y=0, relwidth=0.4, relheight=0.3)
    filter_output_frame.place(relx=0.6, rely=0.3, relwidth=0.4, relheight=0.6)
    close_button_frame.place(x=0, rely=0.9, relwidth=1, relheight=0.1)
    close_tab_button=ttk.Button(close_button_frame,text="CLOSE", command=close_current_tab).pack(pady=5)

    name_label = ttk.Label(info_frame, text = f"Nombre: {name}", font = "Calibri 14 bold").pack()
    ingredients = get_ingredients(recipe)
    ingredients_str = "\n".join(ingredients)
    
    list_of_ingredients = ttk.StringVar(value = ingredients_str)
    ingredients_label=ttk.Label(info_frame, text="Ingredientes:", font="Calibri 12").pack()
    ingredients_list =tk.Listbox(info_frame, height = 10, width = 30, listvariable = list_of_ingredients, font="Calibri 12").pack()
    #scrollbar = ttk.Scrollbar(info_frame,orient=tk.VERTICAL, command=ingredients_list.yview)
    #scrollbar.place(x=ingredients_list.winfo_x()+ingredients_list.winfo_width()+3, y=20, height=20)
    #ingredients_list.unbind("<<ListboxSelect>>",my_click_on_search_results)
    time = recipe["TotalTime"]
    time_label = ttk.Label(info_frame, text = f"Tiempo de cocina: {time}", font = "Calibri 12").pack()
    rating = recipe["AggregatedRating"]
    rating_label = ttk.Label(info_frame, text = f"Rating: {rating}", font = "Calibri 12").pack()
    calories = recipe["Calories"]
    calories_label = ttk.Label(info_frame, text = f"Calories: {calories}", font = "Calibri 12").pack()
    fat = recipe["FatContent"]
    fat_label = ttk.Label(info_frame, text = f"Fat: {fat}", font = "Calibri 12").pack()
    cholesterol = recipe["CholesterolContent"]
    cholesterol_label = ttk.Label(info_frame, text = f"Cholesterol: {cholesterol}", font = "Calibri 12").pack()
    carbohydrate = recipe["CarbohydrateContent"]
    carbohydrate_label = ttk.Label(info_frame, text = f"Carbohydrate: {carbohydrate}", font = "Calibri 12").pack()
    sugar = recipe["SugarContent"]
    sugar_label = ttk.Label(info_frame, text = f"Sugar: {sugar}", font = "Calibri 12").pack()
    protein = recipe["ProteinContent"]
    protein_label = ttk.Label(info_frame, text = f"Protein: {protein}", font = "Calibri 12").pack()
    servings = recipe["RecipeServings"]
    servings_label = ttk.Label(info_frame, text = f"Servicios: {servings}", font = "Calibri 12").pack()

    ### Filter menu frame ###############################################################################
    label_menu=ttk.Label(filter_menu_frame, text="Buscar recetas similares usando:", font="Calibri 14 bold").place(relx=0,rely=0.1)

    check_box_filtro_pmi_status=ttk.IntVar(value=0)
    check_box_filtro_nutricional_status=ttk.IntVar(value=0)
    check_box_filtro_reviews_status=ttk.IntVar(value=0)

    check_box_filtro_pmi=ttk.Checkbutton(
        filter_menu_frame,
        text="Filtro PMI",
        variable=check_box_filtro_pmi_status).place(relx=0,rely=0.3)
    check_box_filtro_nutricional=ttk.Checkbutton(
        filter_menu_frame,
        text="Filtro nutricional",
        variable=check_box_filtro_nutricional_status).place(relx=0.5,rely=0.3)
    check_box_filtro_reviews=ttk.Checkbutton(
        filter_menu_frame,
        text="Filtro por reviews",
        variable=check_box_filtro_reviews_status)
    if recipe["ReviewCount"]>=10:
        check_box_filtro_reviews.place(relx=0,rely=0.5)
    else:
        note_label=ttk.Label(filter_menu_frame,text="**Filtro de reviews no disponible en recetas\ncon menos de 10 reseñas.",
                            font="Calibri 8").place(relx=0,rely=0.5)
   
    filter_button=ttk.Button(filter_menu_frame,
                            text="Search",
                            command = lambda: filtro(df_recipes,name,filter_output_frame,check_box_filtro_pmi_status,check_box_filtro_nutricional_status,check_box_filtro_reviews_status)).place(relx=0.4,rely=0.9,anchor=tk.CENTER)
         
def my_click_on_coincidences_table(my_widget):
    window = my_widget.widget
    index = int(window.curselection()[0])
    value = window.get(index)
    input_recipe.set(value)
    list.delete(0, tk.END)
    coincidences_frame.pack_forget()

def get_data(*args):
    if check_box_state.get() != 1:
        coincidences_frame.pack(pady = 10, side = "bottom")
        list.pack(pady = 5)

        search_str = search_field.get() # user entered string
        list.delete(0, tk.END)
        names = df_recipes["Name"].to_list()
        for name in names:
            if(re.match(search_str, name, re.IGNORECASE)):
                list.insert(tk.END, name)


# Seguimiento de la entrada por el usuario
input_recipe.trace("w", get_data)
list.bind("<<ListboxSelect>>", my_click_on_coincidences_table)

def main():
    window.mainloop()

if __name__ == "__main__":
    main()