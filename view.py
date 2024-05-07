import tkinter as tk
import customtkinter as ctk
from tkinter import *
import tkinter.font as tkFont
from control import Controller
from PIL import Image

""" Interfaz gráfica de la aplicación """

# Style variables
colors = {
    'main' : '#FAFAFA',
    'accent_1' : '#DAE2FF',
    'accent_2' : '#CCC8F1',
    'accent_3' : '#7C73E6',
    'text' : '#8A72B1'
}

icon_diameter = 80
chat_width = 700

root = ctk.CTk()

""" Helper functions """

# Returns the maximum width necessary to fit the text in one line
def line_width(text, font=tkFont.Font(family='Arial', size=14), textbox_width=chat_width):
    return font.measure(text) + 1.5

# Calcula el numero de lineas que ocupa el texto
def compute_number_of_lines(text, font=tkFont.Font(family='Arial', size=14), textbox_width=chat_width):
    # Get the width of a single character in the font
    char_width = font.measure('A')
    
    # Calculate the maximum number of characters per line
    parragraps = text.split('\n')
    max_chars_per_line = int(textbox_width / char_width) if textbox_width > 0 else 1
    num_lines = 0
    for parragraph in parragraps:
        num_lines += ((len(parragraph)) // max_chars_per_line) + 1
    
    return num_lines

# Calcula la altura de cada linea
def font_height(font=tkFont.Font(family='Arial', size=14)):
    height = font.metrics("linespace")
    return height + 10

# Actualiza el ancho del elemento segun el ancho de su master
def update_width(event, master, element, offset=0):
    wrapper_width = master.winfo_width()
    element.config(width = wrapper_width - offset)

""" Ventana principal """
class Window:
    def __init__(self, master):
        controller = Controller()
        self.chat = Main(master, controller, self)
        self.sidebar = Sidebar(master, controller, self)
        # Right border for the sidebar
        divider = tk.Frame(master=master, width=1, height=720, bg=colors['accent_2'])
        divider.pack(fill=tk.BOTH, side=tk.LEFT, expand=False)
        
    def getChatWrapper(self):
        return self.chat.chat
    
    def getHistoryWrapper(self):
        return self.sidebar.history
    
""" Wrapper para el cuadro de chats y barra de mensajes """
class Main:
    def __init__(self, master, controller, window):
        # Background
        self.window = window
        main = tk.Frame(master=master, width=1000, height=730, background=colors['main'])
        main.pack(fill=tk.BOTH, side=tk.RIGHT, expand=True)
        main.update_idletasks()  # Update to ensure accurate dimensions
        # Titulo
        self.title = tk.Label(master=main, height=1, bg=colors['main'], text="Nuevo Chat", font=('Arial', 20, 'bold'), fg=colors['text'])
        self.title.pack(fill=tk.X, side=tk.TOP, expand=True, ipadx=0, ipady=0, pady=0, padx=0)
        # Chats
        self.chat = ChatWrapper(master=main)
        # Bar
        bar = Bar(master=main, controller=controller, main=self)
        # Info Button
        
    def getChatWrapper(self):
        return self.chat
    
    def update_title(self, text):
        self.title.configure(text=text)
    
    def get_title(self):
        return self.title.cget('text')

""" Cuadro de chats """
class ChatWrapper:
    def __init__(self, master):
        self.master = master
        self.chat = ctk.CTkScrollableFrame(master, width=1000, height=640, fg_color=colors['main'])
        self.chat.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
        self.n_chats = 0
        self.chats = []
    
    def add_cupcake_chat(self, text):
        wrapper_1 = tk.Frame(master=self.chat, width=1000, height=60, bg=colors['main'])
        wrapper_2 = tk.Frame(wrapper_1, width=1000, height=60, bg=colors['main'])
        wrapper_2.pack(fill=tk.Y, side=tk.LEFT, expand=False)
        icon_image = ctk.CTkImage(light_image=Image.open('public/logo.png'), size=(icon_diameter, icon_diameter))
        icon = ctk.CTkLabel(master=wrapper_2, width=icon_diameter, height=icon_diameter, image=icon_image, corner_radius = icon_diameter, text="")
        icon.grid(row=0, column=0, padx=10, pady=10)
        content = ctk.CTkTextbox(master=wrapper_2, width=min(chat_width, line_width(text)), fg_color=colors['main'], corner_radius=30, border_width=2, border_color=colors['accent_3'], wrap='word', text_color=colors['accent_3'], font=('Arial', 14))
        content.insert("0.0", text=text)
        # Set max height for chat box
        content.configure(height=min(600, font_height() * compute_number_of_lines(text, textbox_width=min(chat_width, line_width(text)))))
        content.configure(state='disabled')
        content.grid(row=0, column=1, padx=10, pady=10)
        wrapper_1.grid(row=self.n_chats, column=0, padx=0, pady=10, sticky="nsew")
        self.n_chats += 1 # We assume no race condition when trying to write to the chat
        self.chats.append(wrapper_1)
    
    def add_user_chat(self, text):
        wrapper = tk.Frame(master=self.chat, height=60, bg=colors['main'])
        content = ctk.CTkTextbox(master=wrapper, fg_color=colors['accent_2'], corner_radius=30, border_width=0, wrap='word', text_color=colors['main'], font=('Arial', 14))
        content.insert("0.0", text=text)
        padding = tk.Frame(master=wrapper, bg=colors['main'], width=self.chat.winfo_width() -  chat_width - 400) #width=500)#
        # Show
        padding.grid(row=0, column=0)
        content.grid(row=0, column=1)
        wrapper.grid(row=self.n_chats, column=0, padx=10, pady=0, sticky="nsew")
        # Set max height for chat box
        content.configure(width=chat_width) # height=min(600, font_height() * compute_number_of_lines(text, textbox_width=min(chat_width, line_width(text)))),
        content.configure(state='disabled')
        self.n_chats += 1 # We assume no race condition when trying to write to the chat
        self.chats.append(wrapper)
        # Resize dynamically
        #self.master.bind('<Configure>', lambda e: update_width(e, self.chat, element=padding, offset=content.winfo_width() + 20))

""" Barra para enviar mensajes """
class Bar:
    def __init__(self, master, controller, main):
        self.main = main
        self.controller = controller
        # Background
        bar = tk.Frame(master, width=1000, height=80, bg=colors['accent_1'])
        bar.pack(fill=tk.BOTH, side=tk.BOTTOM)
        # Padding
        padding = tk.Frame(master=bar, width=30, bg=colors['accent_1'])
        padding.grid(row=0, column=0)
        # Text Input
        text_input = ctk.CTkEntry(master=bar, placeholder_text="Escribe un mensaje...", width=800, font=('Arial', 12, 'bold'), fg_color='white', text_color=colors['text'], corner_radius=10, border_width=0)
        text_input.grid(row=0, column=1, sticky="nsew", padx=10, pady=10, ipady=5, ipadx=5)
        
        def send_message():
            text = text_input.get()
            # Update title of new chats (if any)
            if self.main.window.sidebar.get_empty_chat() != None and self.main.get_title() == "Nuevo Chat":
                self.main.window.sidebar.update_chat_name("Hoy", "Nuevo Chat", text)
                self.main.update_title(text)
            text_input.delete(0, tk.END)
            self.controller.responder(text, self.main.getChatWrapper())
            
        text_input.bind('<Return>', lambda e: send_message()) # Send question when Enter key is pressed
        # Send Button
        send_button = ctk.CTkButton(master=bar, text="Enviar", font=('Arial', 12), text_color=colors['main'], fg_color=colors['accent_3'], hover_color=colors['accent_2'],corner_radius=40, command=send_message)
        send_button.grid(row=0, column=2 , padx=10, pady=10, ipady=5, ipadx=5)
        send_button.configure(font=('Arial', 12, 'bold'))
     
""" Barra lateral (historial) """   
class Sidebar:
    def __init__(self, master, controller, window):
        # Set class variables
        self.master = master
        self.controller = controller
        self.currentChat = None
        self.window = window
        # Background
        sidebar = tk.Frame(master=master, width=278, height=720, bg=colors['main'])
        sidebar.pack(fill=tk.BOTH, side=tk.LEFT, expand=False)
        # Prevent sidebar from expanding or shrinking
        sidebar.pack_propagate(False)
        # Title
        title = tk.Frame(master=sidebar, width=278, height=80, bg=colors['main'])
        title.pack(fill=tk.BOTH, side=tk.TOP)
        title_text = ctk.CTkLabel(master=title, text="Tus Chats", font=('Arial', 20, 'bold'), fg_color=colors['main'], text_color=colors['text'])
        title_text.pack(fill=tk.BOTH, side=tk.TOP, padx=10, pady=20)
        # History Wrapper
        self.history = ctk.CTkScrollableFrame(master=sidebar, width=278, fg_color=colors['main'])
        self.history.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
        # List of days
        self.days = {}
        self.labels = {}
        # New chat button
        def new_chat():
            # Fecha
            date = "Hoy"
            # Añadir nuevo chat solo si aun no hemos preguntado nada en el chat actual
            # El día existe y el último chat no es "Nuevo Chat"
            if date in self.days.keys():
                new = False
                # Comprobar si hay algun chat con el nombre "Nuevo Chat"
                for chat in self.labels.keys():
                    if chat == "Nuevo Chat":
                        new = True
                if new:
                    return self.currentChat
                else:
                    new_chat = self.add_chat_to_day(date, "Nuevo Chat")
                    controller.hide_chats(window.chat.getChatWrapper())
                    controller.nuevo_chat()
                    return new_chat
            else:
                new_chat = self.add_chat_to_day(date, "Nuevo Chat")
                controller.hide_chats(window.chat.getChatWrapper())
                controller.nuevo_chat()
                return new_chat
                
        # setup button
        button = ctk.CTkButton(master=sidebar, text="Nuevo Chat     +", font=('Arial', 12, 'bold'), text_color=colors['accent_3'], fg_color=colors['accent_1'], hover_color=colors['accent_2'], corner_radius=40, command=new_chat)        
        button.pack(fill=tk.BOTH, side=tk.BOTTOM, padx=10, pady=10, ipady=5, ipadx=5)
        # Show history
        controller.show_history(self)
        # New chat
        self.currentChat = new_chat()
    
    def create_history_entry(self, day, date, text, filename):
        # Define a helper function to capture the current value of filename
        def switch(filename, title):
            self.window.chat.update_title(title)
            self.controller.switch_chat(filename, self.window.getChatWrapper())
        
        def switch_chat_wrapper(filename, title):
            return lambda: switch(filename, title)
        
        def delete(filename, chat_label, date, text):
            return lambda: self.delete_chat(filename, chat_label, date, text)
        wrapper = tk.Frame(master=day, bg=colors['main'])
        title = text[:10]
        label = ctk.CTkButton(master=wrapper, font=('Arial', 14), text=title, fg_color=colors['main'], text_color=colors['text'], anchor='w', corner_radius=10, hover_color=colors['accent_1'], command= switch_chat_wrapper(filename, title))
        delete_button = ctk.CTkButton(master=wrapper, text="Borrar", font=('Arial', 12), fg_color=colors['main'], text_color=colors['text'], anchor='w', corner_radius=10, hover_color=colors['accent_1'], command= delete(filename, wrapper, date, text))
        
        label.grid(row=0, column=0, sticky="nsew")
        delete_button.grid(row=0, column=1, sticky="nsew")
        wrapper.pack(fill=tk.BOTH, side=tk.TOP, padx=10, expand=False)

        if date == "Hoy":
            self.labels[label] = wrapper
        
        return wrapper

    def add_day(self, date, texts, filenames):
        day = tk.Frame(master=self.history, width=278, height=60, bg=colors['main'])
        day.pack(fill=tk.BOTH, side=tk.TOP, pady=10)
        day_text = ctk.CTkLabel(master=day, text=date, font=('Arial', 12), fg_color=colors['main'], text_color=colors['text'], anchor='w')
        day_text.pack(fill=tk.BOTH, side=tk.TOP, padx=10, pady=0, expand=False)
        chat_labels = []

        for i in range(len(texts)):
            # Create the button with the switch_chat_wrapper function
            chat_label = self.create_history_entry(day, date, texts[i], filenames[i])
            chat_labels.append(chat_label)      

        self.days[date] = day
        
        return chat_labels

    def add_chat_to_day(self, date, text):
        up_date = date
        if date == "Hoy":
            up_date = self.controller.get_today_date()
        elif date == "Ayer":
            up_date == self.controller.get_yesterday_date()
        filename = self.controller.get_new_chat_filename(up_date)
        if date in self.days.keys():
            # Add chat to day
            day = self.days[date]
            chat_label = self.create_history_entry(day, date, text, filename)
        else:
            # Create day and add chat
            chat_label = self.add_day(date, [text], [filename])[0]
        return chat_label
            
    def update_chat_name(self, date, old_text, new_text):
        if date == "Hoy":
            for label in self.labels.keys():
                if label.cget('text') == old_text:
                    label.configure(text=new_text[:10])
                    break
                
    def delete_chat(self, filename, chat_label, date, text):
        # Borrar
        self.controller.delete_chat(filename)
        # Actualizar
        chat_label.destroy()
        if date in self.days.keys():
            day = self.days[date]
            if len(day.winfo_children()) == 1:
                day.destroy()
                del self.days[date]
        # Si el chat borrado es el actual, ocultar el chat
        if self.currentChat.cget('text') == text:
            self.controller.hide_chats(self.window.getChatWrapper())
             
    # Returns none if there is no empty chat, and the chat otherwise   
    def get_empty_chat(self):
        if "Hoy" in self.days.keys():
            for label in self.labels.keys():
                if label.cget('text') == "Nuevo Chat":
                    return self.labels[label]
        else:
            return None
        
""" Aplicación  """
class App:
    def __init__(self):
        # Set window attributes
        root.title("Cupcake Chatbot")
        root.geometry("1280x720")  # Default window size
        root.minsize(1280, 720)  # Minimum window size
        # Add elements of gui
        win = Window(root)
        # show window
        root.mainloop()