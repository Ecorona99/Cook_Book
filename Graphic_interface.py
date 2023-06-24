import tkinter as tk
import ttkbootstrap as ttk
from PIL import Image, ImageTk
import pandas as pd
import re
from Graph_Crafting import calculate_PMI_neighbors, get_recipe_id

def search_recipe_by_name(df_recipes, input_recipe):

    button_status.set("Searching...")
    
    df_recipes, recipe = calculate_PMI_neighbors(get_recipe_id(df_recipes, str(input_recipe.get())))
    output_frame=ttk.Frame(window)
    output_label=ttk.Label(output_frame, text = "Mejores coincidencias filtro PMI: ", font = "Calibri 30 bold")


    list_var = ttk.StringVar(value = df_recipes["Name"].to_list())
    results_list=tk.Listbox(output_frame, height = 20, width = 70, listvariable = list_var)
    output_frame.pack(pady = 5)
    output_label.pack(pady = 5)
    results_list.pack(pady = 5)

    button_status.set("Search")


def main():
    window.mainloop()

window=tk.Tk()
window.title("Cook-book V1.0")
window.geometry("1280x720")
input_frame=ttk.Frame(window)

df_recipes = pd.read_parquet("cleaned_recipes.parquet")
names = df_recipes["Name"].to_list()

photo = Image.open("sources/background.jpg")
backgroung_image = ImageTk.PhotoImage(photo)
background_label = ttk.Label(window, image = backgroung_image)
background_label.place(x=0,y=0)
background_label.lower()

input_label=ttk.Label(input_frame, text = "Receta a buscar (id): ", font = "Calibri 20 bold")
input_label.place(y=10)
input_recipe=ttk.StringVar()
search_field=ttk.Entry(input_frame, textvariable = input_recipe)
search_field.place(y=40)
button_status=ttk.StringVar()
button_status.set("Search")
search_button=ttk.Button(input_frame, textvariable = button_status, command = lambda: search_recipe_by_name(df_recipes, search_field))

def my_click(my_widget):
    window = my_widget.widget
    index = int(window.curselection()[0])
    value = window.get(index)
    input_recipe.set(value)
    list.delete(0,tk.END)

def my_down(my_widget):
    list.focus()
    list.selection_set(0)


list = tk.Listbox(window, height = 6, font = "Calibri 15 bold ", relief = 'flat',
                  bg = "SystemButtonFace" , highlightcolor = "SystemButtonFace")

def get_data(*args):
    search_str = search_field.get() # user entered string
    list.delete(0,tk.END)
    for name in names:
        if(re.match(search_str, name, re.IGNORECASE)):
            list.insert(tk.END, name)
list.bind("<<ListboxSelect>>", my_click)
list.bind("<Down>", my_down)
input_recipe.trace("w", get_data)


input_label.pack(pady = 5)
search_field.pack(pady = 10, side = "left")
search_button.pack(pady = 10,side = "right")
input_frame.pack()
list.pack()

if __name__ == "__main__":
    main()