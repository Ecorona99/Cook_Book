import tkinter as tk
import ttkbootstrap as ttk
import time
import Graph_Crafting

def search_recipe_by_name():

    button_status.set("Searching...")
    #revisa si asi se guardan los valores de return de la funcion
    (df_recipes, recipe)=Graph_Crafting.calculate_PMI_neighbors(input_recipe.get())
    output_frame=ttk.Frame(window)
    output_label=ttk.Label(output_frame,text="Mejores coincidencias: ", font="Calibri 20 bold")
    #aqui lo importante es que en value se guarde la lista de nombres de las recetas que estan en el df
    list_var=ttk.StringVar(value=df_recipes["nombre de la columna aqui"])
    results_list=tk.Listbox(output_frame,height=10,width=70,listvariable=list_var)
    output_frame.pack(pady=5)
    output_label.pack(pady=5)
    results_list.pack(pady=5)

    button_status.set("Search")


def main():
    window.mainloop()

window=tk.Tk()
window.title("Cook-book V1.0")
window.geometry("640x400")

input_frame=ttk.Frame(window)

input_label=ttk.Label(input_frame,text="Receta a buscar (id): ", font="Calibri 20 bold")
input_recipe=ttk.StringVar()
search_field=ttk.Entry(input_frame,textvariable=input_recipe)
button_status=ttk.StringVar()
button_status.set("Search")
search_button=ttk.Button(input_frame,textvariable=button_status,command=search_recipe_by_name)

input_label.pack(pady=5)
search_field.pack(pady=10,side="left")
search_button.pack(pady=10,side="right")
input_frame.pack()





if __name__ == "__main__":
    main()