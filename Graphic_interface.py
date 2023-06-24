import tkinter as tk
import ttkbootstrap as ttk
from PIL import Image, ImageTk
import pandas as pd
import re
from Graph_Crafting import calculate_PMI_neighbors, get_recipe_id, calculate_ingredient_similarity

df_recipes = pd.read_parquet("cleaned_recipes.parquet")
names = df_recipes["Name"].to_list()

def search_recipe_by_name(df_recipes, input_recipe):

    button_status.set("Searching...")
    window.update()

    df_recipes, recipe = calculate_PMI_neighbors(get_recipe_id(df_recipes, str(input_recipe.get())))

    output_window=ttk.Toplevel()
    output_window.geometry("640x400")
    output_window_height=output_window.winfo_height()
    output_window_width=output_window.winfo_width()
    output_window.title("Mejores coincidencias filtro PMI")
    output_frame=ttk.Frame(output_window)
    output_label=ttk.Label(output_frame, text = "Mejores coincidencias filtro PMI: ", font = "Calibri 20 bold")
    list_var = ttk.StringVar(value = names)
    results_list=tk.Listbox(output_frame, height = 20, width = 70, listvariable = list_var)
    output_frame.place(x=output_window_width/2, y=output_window_height/2)
    output_label.pack(pady = 5)
    results_list.pack(pady = 5)

    button_status.set("Search")

# Main window
window=tk.Tk()
window.title("Cook-book V1.0")
window.geometry("640x400")
window.update_idletasks()
window_height=window.winfo_height()
window_width=window.winfo_width()

# Background
photo = Image.open("sources/background.jpg")
backgroung_image = ImageTk.PhotoImage(photo)
background_label = ttk.Label(window, image = backgroung_image)
background_label.place(x=0,y=0)
background_label.lower()

# Input Frame
input_frame=ttk.Frame(window)
input_label=ttk.Label(input_frame,width=20, text = "Receta a buscar: ", font = "Calibri 20 bold")
input_recipe=ttk.StringVar()
search_field=ttk.Entry(input_frame, textvariable = input_recipe,width=35)
button_status=ttk.StringVar()
button_status.set("Search")
search_button=ttk.Button(input_frame, textvariable = button_status, command = lambda: search_recipe_by_name(df_recipes, search_field))
coincidences_frame=ttk.Frame(window,name="coincidences_frame")

input_frame.place(x=window_width//2, y=window_height//5,anchor=tk.CENTER)
input_label.pack(pady = 5)
search_field.pack(pady = 10, side="left")
search_button.pack(pady = 10,side = "right")

list = tk.Listbox(coincidences_frame, height = 6, width=50 , font = "Calibri 10 bold ", relief = 'flat',
                  bg = "SystemButtonFace" , highlightcolor = "SystemButtonFace")


def my_click(my_widget):
    window = my_widget.widget
    index = int(window.curselection()[0])
    value = window.get(index)
    input_recipe.set(value)
    list.delete(0,tk.END)
    coincidences_frame.pack_forget()

def my_down(my_widget):
    list.focus()
    list.selection_set(0)

def get_data(*args):
      
    coincidences_frame.pack(pady=10,side="bottom")
    list.pack( pady=5)

    search_str = search_field.get() # user entered string
    list.delete(0,tk.END)
    for name in names:
        if(re.match(search_str, name, re.IGNORECASE)):
            list.insert(tk.END, name)

# Seguimiento de la entrada por el usuario
input_recipe.trace("w", get_data)
list.bind("<<ListboxSelect>>", my_click)
list.bind("<Down>", my_down)


def main():
    window.mainloop()

if __name__ == "__main__":
    main()