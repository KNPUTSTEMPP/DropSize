import cv2
import math
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog, simpledialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv
import os

class BubbleDetectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DropSize")

        # --- Przyciski i interfejs ---
        # Górny kontener na przyciski
        top_frame = tk.Frame(root)
        top_frame.pack(fill=tk.X, padx=20)

        # Środkowy kontener na przyciski
        middle_frame = tk.Frame(root)
        middle_frame.pack(fill=tk.X, padx=20)

        # Dolny kontener na przyciski i etykietę
        bottom_frame = tk.Frame(root)
        bottom_frame.pack(fill=tk.X, padx=20)

        # Przyciski w górnym kontenerze
        self.btn_select = tk.Button(top_frame, text="Wybierz obraz", command=self.load_image)
        self.btn_select.pack(pady=10, anchor="center")

        # Wybierz skalę powiększenia obrazu
        tk.Label(top_frame, text = "Powiększenie obrazu",anchor="center").pack()
        self.image_xscale_var = tk.StringVar(value='10x')
        self.scale_values_dropdown = ['2x', '4x', '10x','40x','100x']
        self.scale_menu = tk.OptionMenu(top_frame,self.image_xscale_var,*self.scale_values_dropdown,command=self.scale_changed)
        self.scale_values_map = {'2x':0.002680, '4x':0.001340, '10x':0.000532, '40x':0.000134, '100x':0.0000536}
        self.scale_menu.pack(pady=5)

        tk.Label(top_frame, text="--- LUB ustaw ręcznie ---", fg="#555").pack(pady=5)

        tk.Label(top_frame, text="Skala obrazu [µm/piksel]:", anchor="center").pack()
        self.scale_var = tk.DoubleVar(value=0.000532)  
        self.scale_entry = tk.Entry(top_frame, textvariable=self.scale_var, width=10, justify="center")
        self.scale_entry.pack(pady=5)
        
  
        self.btn_enter_scale = tk.Button(top_frame, text="Wpisz skalę", command=self.enter_scale)
        self.btn_enter_scale.pack(pady=5)

        self.btn_set_scale = tk.Button(top_frame, text="Ustal skalę ręcznie", command=self.measure_scale)
        self.btn_set_scale.pack(pady=5)

        # Przyciski w środkowym kontenerze
        self.btn_run = tk.Button(middle_frame, text="Uruchom detekcję", command=self.run_detection, bg="#ff9999")
        self.btn_run.pack(pady=10)

        self.btn_add_bubble = tk.Button(middle_frame, text="Dodaj kroplę", command=self.add_bubble)
        self.btn_add_bubble.pack(pady=5)

        self.btn_save = tk.Button(middle_frame, text="Zapisz wyniki do CSV", command=self.save_results_manually)
        self.btn_save.pack(pady=5)

        self.btn_save_image = tk.Button(middle_frame, text="Zapisz obraz z obrysami", command=self.save_detected_image)
        self.btn_save_image.pack(pady=5)

        frame_hist = tk.Frame(middle_frame)
        frame_hist.pack(pady=10)

        tk.Label(frame_hist, text="Histogram średnic kropel:", anchor="center").pack()
        self.btn_hist = tk.Button(frame_hist, text="Histogram ilościowy", command= lambda: self.show_histogram(type='count'))
        self.btn_hist.pack(side=tk.LEFT,pady=5)

        self.btn_hist_freq = tk.Button(frame_hist, text="Histogram częstościowy", anchor="center", command=lambda: self.show_histogram(type='frequency'))
        self.btn_hist_freq.pack(side=tk.LEFT,pady=5)

        # Etykieta w dolnym kontenerze
        self.label = tk.Label(bottom_frame, text="Załaduj obraz i kliknij 'Uruchom detekcję'", font=("Arial", 11, "bold"), anchor="center")
        self.label.pack(pady=5)

        # --- Układ główny ---
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Kontener na canvas z obrazem
        self.canvas_frame = tk.Frame(self.main_frame)
        self.canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20)

        # Kontener na średnicę Sautera
        self.sauter_frame = tk.Frame(self.main_frame, width=160, bg="#f0f0f0")
        self.sauter_frame.pack(side=tk.RIGHT, fill=tk.Y)
        self.sauter_frame.pack_propagate(False)

        self.canvas = None
        self.figure = None
        self.sauter_label = None

        self.image_path = None
        self.bubble_circles = []

    # --- Zmiana skali z menu ---
    def scale_changed(self, key):
        if key in self.scale_values_map:
            new_scale = self.scale_values_map[key]
            self.scale_var.set(new_scale)

    # --- Wczytanie obrazu ---
    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Obrazy", "*.jpg *.png *.bmp")])
        if file_path:
            self.image_path = file_path
            self.label.config(text=f"Wybrano plik: {os.path.basename(file_path)}", fg="green")
            # Zmiana tła przycisku na zielone po załadowaniu zdjęcia
            self.btn_run.config(bg="#90ee90")

    # --- Detekcja automatyczna ---
    def run_detection(self):
        if not self.image_path:
            self.label.config(text="Nie wybrano pliku!", fg="red")
            return

        try:
            scale = float(self.scale_var.get())
            if scale <= 0:
                raise ValueError
        except ValueError:
            self.label.config(text="Nieprawidłowa wartość skali!", fg="red")
            return

        im = cv2.imread(self.image_path)
        imgray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
        im_gauss = cv2.GaussianBlur(imgray, (7, 7), 0)
        _, thresh = cv2.threshold(im_gauss, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        kernel = np.ones((3, 3), np.uint8)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        contours_data = []
        for con in contours:
            perimeter = cv2.arcLength(con, True)
            area = cv2.contourArea(con)
            if perimeter == 0:
                continue
            circularity = 4 * math.pi * (area / (perimeter * perimeter))
            if 0.5 < circularity < 1.5 and area > 20:
                (x, y), radius = cv2.minEnclosingCircle(con)
                contours_data.append({'center': (x, y), 'radius': radius})

        contours_data.sort(key=lambda c: c['radius'], reverse=True)
        final_circles = []
        circles_data = []

        for data in contours_data:
            x, y = data['center']
            r = data['radius']
            keep = True
            for existing in final_circles:
                ex, ey = existing['center']
                er = existing['radius']
                if math.hypot(x - ex, y - ey) < er * 0.8:
                    keep = False
                    break
            if keep:
                final_circles.append(data)
                micrometers = 2 * r * scale
                circles_data.append((len(circles_data)+1, micrometers))

        self.bubble_circles = final_circles
        self.draw_bubbles()
        self.update_sauter_label(circles_data)
        self.label.config(text="Detekcja zakończona - kliknij kroplę, aby ją usunąć", fg="green")

        # Kliknięcie usuwa kroplę
        def on_click(event):
            if event.xdata is None or event.ydata is None:
                return
            x_click, y_click = event.xdata, event.ydata

            removed = False
            for i, bubble in enumerate(self.bubble_circles[:]):
                x, y = bubble['center']
                r = bubble['radius']
                if math.hypot(x - x_click, y - y_click) <= r:
                    del self.bubble_circles[i]
                    removed = True
                    break

            if not removed:
                return

            self.redraw_bubbles()
            new_data = [(i + 1, 2 * b['radius'] * scale) for i, b in enumerate(self.bubble_circles)]
            self.update_sauter_label(new_data)
            self.label.config(text="Zaktualizowano dane po usunięciu kropli", fg="blue")

        self.figure.canvas.mpl_connect('button_press_event', on_click)


    # --- Zapis CSV ---
    def save_results_manually(self):
        if not self.bubble_circles:
            self.label.config(text="Brak danych do zapisania!", fg="red")
            return

        # Oblicz aktualne dane na podstawie zapisanych kropel i skali
        scale = self.scale_var.get()
        circles_data = [(i + 1, 2 * b['radius'] * scale) for i, b in enumerate(self.bubble_circles)]

        # Otwórz okno dialogowe zapisu
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Pliki CSV", "*.csv"), ("Wszystkie pliki", "*.*")],
            title="Zapisz wyniki pomiarów"
        )

        if not file_path:
            return  # Użytkownik anulował zapis

        try:
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Indeks", "Średnica (mikrometry)"])
                for index, diameter in circles_data:
                    writer.writerow([index, round(diameter, 2)])
            
            self.label.config(text=f"Zapisano wyniki w: {os.path.basename(file_path)}", fg="green")
        except Exception as e:
            self.label.config(text=f"Błąd zapisu: {e}", fg="red")


    # --- Rysowanie kropli ---
    def draw_bubbles(self):
        im = cv2.imread(self.image_path)
        im_rgb = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)

        for bubble in self.bubble_circles:
            x, y = bubble['center']
            r = int(bubble['radius'])
            cv2.circle(im_rgb, (int(x), int(y)), r, (0, 255, 0), 2)

        if self.figure:
            self.canvas.get_tk_widget().destroy()

        self.figure = plt.Figure(figsize=(8, 6))
        ax = self.figure.add_subplot(111)
        ax.imshow(im_rgb)
        ax.set_title("Wykryte krople")
        ax.axis("off")

        self.canvas = FigureCanvasTkAgg(self.figure, master=self.canvas_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


    # --- Odświeżanie widoku ---
    def redraw_bubbles(self):
        if self.figure is None:
            return
        ax = self.figure.axes[0]
        ax.clear()

        output = cv2.imread(self.image_path)
        output = cv2.cvtColor(output, cv2.COLOR_BGR2RGB)

        for bubble in self.bubble_circles:
            x, y = bubble['center']
            r = int(bubble['radius'])
            cv2.circle(output, (int(x), int(y)), r, (0, 255, 0), 2)

        ax.imshow(output)
        ax.set_title("Wykryte krople")
        ax.axis("off")
        self.canvas.draw()


    # --- Aktualizacja średnicy Sautera ---
    def update_sauter_label(self, circles_data):
        diameters = [d for _, d in circles_data]
        if self.sauter_label:
            self.sauter_label.destroy()

        if diameters:
            numerator = sum([d**3 for d in diameters])
            denominator = sum([d**2 for d in diameters])
            d32 = numerator / denominator if denominator != 0 else 0
            self.sauter_label = tk.Label(
                self.sauter_frame,
                text=f"średnica Sautera\nd = {d32:.5f} µm",
                font="TkDefaultFont", fg="blue", anchor="center", justify="center",
                relief=tk.RAISED, bg="#f0f0f0"
            )
        else:
            self.sauter_label = tk.Label(
                self.sauter_frame,
                text="Brak wykrytych kropel",
                font="TkDefaultFont", fg="red", anchor="center", justify="center",
                relief=tk.RAISED, bg="#f0f0f0"
            )

        self.sauter_label.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9)


    # --- Dodanie nowej kropli ręcznie ---
    def add_bubble(self):
        if not self.image_path:
            self.label.config(text="Nie wybrano obrazu!", fg="red")
            return

        scale = self.scale_var.get()
        if scale <= 0:
            self.label.config(text="Nieprawidłowa wartość skali!", fg="red")
            return

        im = cv2.imread(self.image_path)
        im_rgb = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
        for bubble in self.bubble_circles:
            x, y = bubble['center']
            r = int(bubble['radius'])
            cv2.circle(im_rgb, (int(x), int(y)), r, (0, 255, 0), 2)

        h, w = im.shape[:2]
        plt.figure("Dodaj krople - kliknij środek, potem krawędź kropli")
        plt.imshow(im_rgb, extent=(0, w, h, 0))
        plt.title("Kliknij środek kropli, a następnie punkt na jego krawędzi")
        points = plt.ginput(2)
        plt.close()

        if len(points) < 2:
            self.label.config(text="Nie wybrano dwóch punktów!", fg="red")
            return

        (x1, y1), (x2, y2) = points
        radius_px = math.hypot(x2 - x1, y2 - y1)
        if radius_px <= 0:
            self.label.config(text="Promień nie może być zerowy!", fg="red")
            return

        micrometers = 2 * radius_px * scale

        new_bubble = {'center': (x1, y1), 'radius': radius_px}
        self.bubble_circles.append(new_bubble)
        
        # Sortowanie kroepl po wielkości (od największej)
        self.bubble_circles.sort(key=lambda b: b['radius'], reverse=True)
        
        # Aktualizacja danych i pliku CSV
        circles_data = [(i + 1, 2 * b['radius'] * scale) for i, b in enumerate(self.bubble_circles)]
        
        # Przerysowanie kropel i aktualizacja etykiety Sautera
        self.redraw_bubbles()
        self.update_sauter_label(circles_data)

        self.label.config(text=f"Dodano kroplę o średnicy {micrometers:.2f} µm (zaktualizowano plik)", fg="green")


    # --- Wyznaczanie skali obrazu ---
    def measure_scale(self):
        if not self.image_path:
            self.label.config(text="Nie wybrano obrazu!", fg="red")
            return

        im = cv2.imread(self.image_path)
        im_rgb = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
        h, w = im.shape[:2]

        plt.figure("Ustal skalę – kliknij dwa punkty o znanej odległości")
        plt.imshow(im_rgb, extent=(0, w, h, 0))
        plt.title("Kliknij dwa punkty o znanej odległości (w µm)")
        points = plt.ginput(2,timeout=120)
        plt.close()

        if len(points) < 2:
            self.label.config(text="Nie wybrano dwóch punktów!", fg="red")
            return

        (x1, y1), (x2, y2) = points
        distance_px = math.hypot(x2 - x1, y2 - y1)
        if distance_px == 0:
            self.label.config(text="Punkty są zbyt blisko!", fg="red")
            return

        real_distance = simpledialog.askfloat("Odległość rzeczywista", "Podaj odległość między punktami w µm:")
        if real_distance is None or real_distance <= 0:
            self.label.config(text="Nieprawidłowa wartość!", fg="red")
            return

        scale = real_distance / distance_px
        old_scale = self.scale_var.get()
        self.scale_var.set(scale)
        
        # Aktualizacja danych i plików CSV po zmianie skali
        if self.bubble_circles:
            circles_data = [(i + 1, 2 * b['radius'] * scale) for i, b in enumerate(self.bubble_circles)]
            self.update_sauter_label(circles_data)
            self.label.config(text=f"Skala zmieniona z {old_scale:.3f} na {scale:.3f} µm/piksel. Zaktualizowano dane.", fg="green")
        else:
            self.label.config(text=f"Skala ustawiona: {scale:.3f} µm/piksel", fg="green")


    # --- Histogram średnic ---
    def enter_scale(self):
        """Aktualizuje skalę na podstawie wpisanej wartości i przelicza wszystkie dane"""
        try:
            new_scale = self.scale_var.get()
            if new_scale <= 0:
                self.label.config(text="Nieprawidłowa wartość skali!", fg="red")
                return
                
            # Aktualizacja danych i plików CSV z nową skalą
            if self.bubble_circles:
                circles_data = [(i + 1, 2 * b['radius'] * new_scale) for i, b in enumerate(self.bubble_circles)]
                self.update_sauter_label(circles_data)
                self.label.config(text=f"Skala zaktualizowana na {new_scale:.3f} µm/piksel. Zaktualizowano dane.", fg="green")
            else:
                self.label.config(text=f"Skala ustawiona na {new_scale:.3f} µm/piksel", fg="green")
                
        except tk.TclError:
            self.label.config(text="Wprowadź prawidłową wartość liczbową!", fg="red")
            
    def show_histogram(self,type='count'):
        if not self.bubble_circles:
            self.label.config(text="Brak danych do histogramu!", fg="red")
            return

        scale = self.scale_var.get()
        diameters = [2 * b['radius'] * scale for b in self.bubble_circles]

        total_bubbles = len(diameters)
        bins = 20
        diameters_binned,bin_edges = np.histogram(diameters,bins=bins)
        
        diameters_binned_pct = diameters_binned / total_bubbles * 100

        if type=='count':
            plt.figure("Histogram średnic kropel")
            plt.hist(diameters, bins=bins, color='skyblue', edgecolor='black')
            plt.title("Histogram ilościowy średnic kropel")
            plt.xlabel("Średnica (µm)")
            plt.ylabel("Liczba kropel")
            plt.tight_layout()
            plt.show()

        elif type=='frequency':
            plt.figure("Histogram częstościowy średnic kropel")
            plt.bar(bin_edges[:-1], diameters_binned_pct, width=np.diff(bin_edges), edgecolor='black', align='edge', color='salmon')
            plt.yticks(ticks = plt.yticks()[0],labels = [f"{int(tick)}%" for tick in plt.yticks()[0]])
            plt.title("Histogram częstościowy średnic kropel")
            plt.xlabel("Średnica (µm)")
            plt.ylabel("Częstość występowania")
            plt.tight_layout()
            plt.show()
    
    def save_detected_image(self):
        if not self.image_path or not self.bubble_circles:
            self.label.config(text="Brak obrazu lub detekcji do zapisania!", fg="red")
            return
    
        image = cv2.imread(self.image_path)
        output = image.copy()
    
        # TYLKO obrysy kropel
        for bubble in self.bubble_circles:
            x, y = bubble['center']
            r = int(bubble['radius'])
            cv2.circle(output, (int(x), int(y)), r, (0, 255, 0), 2)
    
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPG", "*.jpg"), ("BMP", "*.bmp")],
            title="Zapisz obraz z obrysami"
        )
    
        if not file_path:
            return
    
        cv2.imwrite(file_path, output)
        self.label.config(text="Zapisano obraz z obrysami", fg="green")



# --- Uruchomienie programu ---
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("900x700")
    app = BubbleDetectorApp(root)
    root.mainloop()