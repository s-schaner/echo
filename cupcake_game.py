import tkinter as tk
import random

class CupcakeGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Cupcake Surprise Game")
        self.buttons = []
        self.message = tk.StringVar()
        self.message.set("Pick a cupcake!")
        self.message_label = tk.Label(master, textvariable=self.message, font=("Arial", 14))
        self.message_label.pack(pady=10)
        self.setup_buttons()
        self.new_round()

    def setup_buttons(self):
        frame = tk.Frame(self.master)
        frame.pack(padx=10, pady=10)
        for i in range(4):
            btn = tk.Button(
                frame,
                text="🧁",
                font=("Arial", 40),
                width=2,
                command=lambda idx=i: self.check_choice(idx)
            )
            btn.grid(row=0, column=i, padx=5, pady=5)
            self.buttons.append(btn)

    def new_round(self):
        self.winner = random.randint(0, 3)
        self.message.set("Pick a cupcake!")

    def check_choice(self, idx):
        if idx == self.winner:
            self.message.set("You found the surprise!")
        else:
            self.message.set("No surprise. Try again!")
        self.new_round()


def main():
    root = tk.Tk()
    game = CupcakeGame(root)
    root.mainloop()

if __name__ == "__main__":
    main()
