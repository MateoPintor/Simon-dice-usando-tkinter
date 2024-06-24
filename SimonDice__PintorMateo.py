import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import json
from datetime import datetime

class Jugador:
    def __init__(self, nombre, puntaje, fecha):
        self.nombre = nombre
        self.puntaje = puntaje
        self.fecha = fecha

    def __gt__(self, other):
        return self.puntaje > other.puntaje

class GestorJugadores:
    def __init__(self):
        self.jugadores = []

    def cargar_puntajes(self):
        try:
            with open("pysimonpuntajes.json", "r") as file:
                scores = json.load(file)
                for score in scores:
                    jugador = Jugador(score["player"], score["score"], score["date"])
                    self.jugadores.append(jugador)
        except FileNotFoundError:
            pass

    def guardar_puntajes(self):
        scores = [{
            "player": jugador.nombre,
            "score": jugador.puntaje,
            "date": jugador.fecha,
        } for jugador in self.jugadores]

        with open("pysimonpuntajes.json", "w") as file:
            json.dump(scores, file, indent=4)

    def agregar_jugador(self, jugador):
        self.jugadores.append(jugador)
        self.jugadores.sort(reverse=True)

    def reset_puntajes(self):
        self.jugadores = []
        with open("pysimonpuntajes.json", "w") as file:
            json.dump([], file)

def darken_color(color, factor=0.7):
    color = color.lstrip('#')
    rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
    
    darker_rgb = tuple(int(c * factor) for c in rgb)
    
    darker_color = '#{:02x}{:02x}{:02x}'.format(*darker_rgb)
    
    return darker_color

class SimonGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Simon Dice")
        self.sequence = []
        self.user_sequence = []
        self.buttons = []
        self.colors = ["#ff0000", "#00ff00", "#0000ff", "#ffff00"]
        self.score = 0

        self.gestor = GestorJugadores()
        self.gestor.cargar_puntajes()
        self.player_name = self.ask_player_name()
        self.create_menu()
        self.create_widgets()
        self.create_player_info()
        self.start_game()

    def ask_player_name(self):
        return simpledialog.askstring("PySimonDice", "Jugador:")
    
    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        options_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Opciones", menu=options_menu)
        options_menu.add_command(label="Ver puntajes", command=self.show_scores)
        options_menu.add_separator()
        options_menu.add_command(label="Salir", command=self.root.quit)

    def create_widgets(self):
        for i, color in enumerate(self.colors):
            button = tk.Canvas(self.root, width=100, height=100, bg=color, relief="raised")
            button.grid(row=i//2 + 3, column=i%2, padx=10, pady=10)
            button.bind("<Button-1>", lambda e, i=i: self.on_button_click(i))
            self.buttons.append(button)

    def create_player_info(self):
        self.player_info_label = tk.Label(self.root, text=f"Jugador: {self.player_name}")
        self.player_info_label.grid(row=0, column=0, sticky="w", padx=10, pady=10)
        self.score_info_label = tk.Label(self.root, text=f"Puntaje: {self.score}")
        self.score_info_label.grid(row=0, column=1, sticky="e", padx=10, pady=10)

    def start_game(self):
        self.sequence = []
        self.user_sequence = []
        self.score = 0
        self.update_player_info()  
        self.root.after(1000, self.next_round)

    def next_round(self):
        delay = 1000
        self.user_sequence = []
        next_color = random.choice(self.buttons)
        self.sequence.append(next_color)
        self.play_sequence(delay)

    def play_sequence(self, delay):
        for i, button in enumerate(self.sequence):
            self.root.after(i * delay, lambda b=button: self.highlight_button(b))
        total_delay = len(self.sequence) * delay
        self.root.after(total_delay, self.start_timer)

    def highlight_button(self, button):
        original_color = button.cget("bg")
        darker_color = darken_color(original_color)
        button.config(bg=darker_color)
        self.root.after(500, lambda: button.config(bg=original_color))

    def on_button_click(self, index):
        self.user_sequence.append(self.buttons[index])
        self.highlight_button(self.buttons[index])
        if self.user_sequence == self.sequence[:len(self.user_sequence)]:
            if len(self.user_sequence) == len(self.sequence):
                self.score += 1
                self.update_player_info()  
                self.root.after(1000, self.next_round)
        else:
            self.game_over()

    def game_over(self):
        messagebox.showinfo("GAME OVER", f"Juego terminado. Puntaje: {self.score}")
        self.save_score()
        self.start_game()

    def save_score(self):
        score_data = {
            "player": self.player_name,
            "score": self.score,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        try:
            with open("pysimonpuntajes.json", "r") as file:
                scores = json.load(file)
        except FileNotFoundError:
            scores = []
        scores.append(score_data)
        with open("pysimonpuntajes.json", "w") as file:
            json.dump(scores, file, indent=4)
        self.gestor.agregar_jugador(Jugador(
            self.player_name,
            self.score,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ))
        self.gestor.guardar_puntajes()

    def update_player_info(self):
        self.player_info_label.config(text=f"Jugador: {self.player_name}")
        self.score_info_label.config(text=f"Puntaje: {self.score}")

    def show_scores(self):
        scores_window = tk.Toplevel(self.root)
        scores_window.title("Galería de puntajes")
        tk.Label(scores_window, text="Jugador", borderwidth=2, relief="ridge", width=20).grid(row=0, column=0)
        tk.Label(scores_window, text="Fecha", borderwidth=2, relief="ridge", width=20).grid(row=0, column=1)
        tk.Label(scores_window, text="Puntaje", borderwidth=2, relief="ridge", width=20).grid(row=0, column=2)
        for i, jugador in enumerate(self.gestor.jugadores):
            tk.Label(scores_window, text=jugador.nombre, borderwidth=2, relief="ridge", width=20).grid(row=i+1, column=0)
            tk.Label(scores_window, text=jugador.fecha, borderwidth=2, relief="ridge", width=20).grid(row=i+1, column=1)
            tk.Label(scores_window, text=jugador.puntaje, borderwidth=2, relief="ridge", width=20).grid(row=i+1, column=2)

if __name__ == "__main__":
    root = tk.Tk()
    game = SimonGame(root)
    root.mainloop()