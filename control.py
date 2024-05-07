import os
import datetime
from model import ChatBot
import json

""" Funciones de control para actualizar el estado de la interfaz de usuario """

class Controller:
    def __init__(self):
        self.bot = ChatBot()
        self.chatWrapper = None
        self.historyWrapper = None
        self.current_chat = None
        
    # Devuelve la fecha de hoy
    def get_today_date(self):
        today = datetime.date.today()
        return today.strftime("%Y-%m-%d")
    
    # Devuelve la fecha de ayer
    def get_yesterday_date(self):
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        return yesterday.strftime("%Y-%m-%d")
    
    # Devuelve el historial de chats en el formato {date: [{"title": title, "file": file}, ...], ...}
    def _get_chat_history(self):
        history_folder = "history"
        chat_history = {}

        for filename in os.listdir(history_folder):
            filepath = os.path.join(history_folder, filename)
            if os.path.isfile(filepath):
                day, month, year, index = filename.split("-")
                date = f"{day.strip()}-{month.strip()}-{year.strip()}"
                index = int(index.split(".")[0])
                title = ""
                
                with open(filepath, "r", encoding="utf-8") as file:
                    title = file.readline().strip()
                
                if date in chat_history:
                    chat_history[date].append({"title": title, "file": filepath})
                else:
                    chat_history[date] = [{"title": title, "file": filepath}]
        
        return chat_history
    
    # Devuelve la respuesta a la pregunta del usuario
    def responder(self, pregunta, chatWrapper):
        chatWrapper.add_user_chat(pregunta)
        respuesta = self.bot.responder(pregunta)
        chatWrapper.add_cupcake_chat(respuesta)
    
    # Crea un historial para un nuevo chat
    def nuevo_chat(self):
        return self.bot.nuevo_chat()
    
    # Elimina el historial de un chat
    def borrar_del_historial(self, date, index):
        # Borrar
        filename = f"{date}-{index}.txt"
        filepath = os.path.join("history", filename)
        if os.path.exists(filepath):
            os.remove(filepath)
    
    # Muestra el historial de chats
    def show_history(self, historyWrapper):
        for date, chats in self._get_chat_history().items():
            if date == self.get_today_date():
                date = "Hoy"
            elif date == self.get_yesterday_date():
                date = "Ayer"
            titles = [json.loads(chat['title'])["question"] for chat in chats]
            filenames = [chat['file'] for chat in chats]
            historyWrapper.add_day(date, titles, filenames)
    
    # Esconde los chats anteriores
    def hide_chats(self, chatWrapper):
        chatWrapper.n_chats = 0
        for slave in chatWrapper.chats:
            slave.destroy()
        chatWrapper.add_cupcake_chat("Hola, soy Cupcake, tu asistente virtual. ¿En qué puedo ayudarte?")
    
    # Muestra el chat seleccionado
    def switch_chat(self, filename, chatWrapper):
        self.current_chat = filename
        try:
            self.hide_chats(chatWrapper)
            memoria = []
            # Leer el chat
            with open(filename, "r", encoding="utf-8") as file:
                lines = file.readlines()
                for line in lines:
                    try:
                        line_data = json.loads(line)
                        # Mostrar chats
                        chatWrapper.add_user_chat(line_data["question"])
                        chatWrapper.add_cupcake_chat(line_data["answer"])
                        # Preparar memoria para pasar modelo
                        chat = (line_data["question"], line_data["answer"])
                        memoria.append(chat)
                    except(json.JSONDecodeError):
                        print("Error al leer el archivo")
            # Actualizar memoria
            self.bot.cargar_chat(filename, memoria)
        except(FileNotFoundError):
            print("No se ha encontrado el archivo")
            self.nuevo_chat()
            
    # Devuelve el nombre del archivo de chat
    def get_new_chat_filename(self, date):
        return self.bot.get_new_chat_filename(date)
    
    # Elimina un chat del historial
    def delete_chat(self, filename):
        print(f"Eliminando {filename}")
        try:
            os.remove(filename)
        except:
            print("No se ha podido eliminar el archivo")