import tkinter as tk
#from tkinter import ttk as nb
import ttkbootstrap as ttk
from PIL import Image, ImageTk
import pandas as pd
import re
from Data_Processing import get_recipe_id, calculate_PMI_neighbors

df_recipes = pd.read_parquet("cleaned_recipes.parquet")
names = df_recipes["Name"].to_list()

def search_recipe_by_name(df_recipes, input_recipe):

    button_status.set("Searching...")
    window.update()

    df_recipes, recipe = calculate_PMI_neighbors(df_recipes, get_recipe_id(df_recipes,input_recipe.get()))

    output_window=ttk.Frame(notebook)
    notebook.add(output_window,text="Resultados de busqueda",sticky="nsew")

    output_window_height = output_window.winfo_height()
    output_window_width = output_window.winfo_width()
    output_frame = ttk.Frame(output_window)
    output_label = ttk.Label(output_frame, text = "Mejores coincidencias filtro PMI: ", font = "Calibri 20 bold")
    list_var = ttk.StringVar(value = names)
    results_list = tk.Listbox(output_frame, height = 20, width = 70, listvariable = list_var)
    close_tab=ttk.Button(output_frame,text="Close",command= lambda: notebook.forget(1))
    output_frame.place(x = output_window_width / 2, y = output_window_height / 2)
    close_tab.pack(pady=5,side="bottom",expand=True)
    output_label.pack(pady = 5,expand=True)
    results_list.pack(pady = 5,expand=True)
    button_status.set("Search")


def check_box_toggle():   
    if check_box_state.get()==1:
        time_frame.place(x=window_width // 2, y=check_box_frame.winfo_height()+check_box_frame.winfo_y()+25,anchor = tk.CENTER)
        time_label.pack(pady=3,side="top",expand=True,fill="x")
        horas_entry_field.pack(pady=3,side="left",expand=True)
        minutos_entry_field.pack(pady=3,side="left",expand=True)
        input_label_text.set("Buscar receta por sus ingredientes")
    else:
        input_label_text.set("Buscar receta por nombre:")
        time_frame.place_forget()
       
        
        
# Main window
window = tk.Tk()
window.title("Cook-book V1.0")
window.geometry("800x600")
window.resizable(0,0)
window.update_idletasks()
notebook=ttk.Notebook(window)
notebook.pack(fill="both",expand=True)
main_tab=ttk.Frame(notebook)
notebook.add(main_tab,text="Buscar")
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
input_label_text=ttk.StringVar(value="Buscar receta por nombre:")
input_label = ttk.Label(input_frame, width = 30, text = "Receta a buscar:", font = "Calibri 18 bold", anchor = tk.CENTER,textvariable=input_label_text)
input_recipe = ttk.StringVar()
search_field = ttk.Entry(input_frame, textvariable = input_recipe)
button_status = ttk.StringVar()
button_status.set("Search")
search_button = ttk.Button(input_frame, textvariable = button_status, command = lambda: search_recipe_by_name(df_recipes, search_field))
# Check box frame
check_box_frame=ttk.Frame(main_tab)
check_box_label=ttk.Label(check_box_frame,text="Buscar por ingrediente",font="Calibri 10")
check_box_state=ttk.IntVar()
check_box=ttk.Checkbutton(check_box_frame,command=check_box_toggle,variable=check_box_state)
# Coincidences frame
coincidences_frame = ttk.Frame(main_tab, name = "coincidences_frame")
# Time Frame
time_frame=ttk.Frame(main_tab)
time_label=ttk.Label(time_frame,text="Limitar tiempo de preparacion(hh/mm)",font="Calibri 12 bold")
horas=ttk.StringVar()
minutos=ttk.StringVar()
horas_entry_field=ttk.Entry(time_frame,textvariable=horas,width=8)
minutos_entry_field=ttk.Entry(time_frame,textvariable=minutos,width=8)

# Packin elements to frames
input_frame.place(x = window_width // 2, y = window_height // 5, anchor = tk.CENTER)
input_label.pack(pady = 5)
search_field.pack(pady = 10, side="left",expand=True,fill="x")
search_button.pack(pady = 10, side = "right")
window.update_idletasks()
check_box_frame.place(x=window_width // 2, y=input_frame.winfo_height()+input_frame.winfo_y()+25,anchor = tk.CENTER)
check_box_label.pack(pady=5)
check_box.pack(pady=5)
window.update()


list = tk.Listbox(coincidences_frame, height = 15, width = 50 , font = "Calibri 10 bold ", relief = 'flat',
                  bg = "SystemButtonFace" , highlightcolor = "SystemButtonFace")


        

def my_click(my_widget):
    window = my_widget.widget
    index = int(window.curselection()[0])
    value = window.get(index)
    input_recipe.set(value)
    list.delete(0, tk.END)
    coincidences_frame.pack_forget()

def get_data(*args):
      
    coincidences_frame.pack(pady = 10, side = "bottom")
    list.pack(pady = 5)

    search_str = search_field.get() # user entered string
    list.delete(0, tk.END)
    for name in names:
        if(re.match(search_str, name, re.IGNORECASE)):
            list.insert(tk.END, name)

# Seguimiento de la entrada por el usuario
input_recipe.trace("w", get_data)
list.bind("<<ListboxSelect>>", my_click)

def main():
    window.mainloop()

if __name__ == "__main__":
    main()