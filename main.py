import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime
import csv
import os
from PIL import Image, ImageTk

class RFIDReaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistem Absensi OMI0001926068")
        self.root.geometry("700x600")
        self.rfid_code = ""
        self.mode = tk.StringVar()
        self.mode.set("Masuk")
        self.database = self.load_database("database_karyawan.txt")
        self.log_filename = "log_omron.csv"
        if not os.path.exists(self.log_filename):
            with open(self.log_filename, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["RFID", "Nama", "Absen", "Mode", "Waktu"])

        tk.Label(root, text="Tempelkan Kartu RFID", font=("Arial", 18)).pack(pady=10)
        frame = tk.Frame(root)
        frame.pack()
        tk.Label(frame, text="Mode: ", font=("Arial", 14)).pack(side=tk.LEFT)
        tk.OptionMenu(frame, self.mode, "Masuk", "Pulang").pack(side=tk.LEFT)
        self.code_label = tk.Label(root, text="", font=("Arial", 16), fg="blue")
        self.code_label.pack(pady=5)
        self.name_label = tk.Label(root, text="", font=("Arial", 16))
        self.name_label.pack(pady=5)
        self.absen_label = tk.Label(root, text="", font=("Arial", 16))
        self.absen_label.pack(pady=5)
        self.time_label = tk.Label(root, text="", font=("Arial", 16), fg="green")
        self.time_label.pack(pady=5)
        self.photo_label = tk.Label(root)
        self.photo_label.pack(pady=5)
        self.listbox = tk.Listbox(root, width=70, height=10)
        self.listbox.pack(pady=10)
        stats_frame = tk.Frame(root)
        stats_frame.pack()
        self.total_label = tk.Label(stats_frame, text="Total Tap: 0", font=("Arial", 12))
        self.total_label.pack(side=tk.LEFT, padx=10)
        tk.Button(stats_frame, text="Export Laporan", command=self.export_laporan).pack(side=tk.LEFT, padx=10)
        tk.Button(stats_frame, text="Reset", command=self.reset_display).pack(side=tk.LEFT, padx=10)
        root.bind("<Key>", self.key_pressed)
        root.focus_set()
        self.load_today_log()

    def load_database(self, filename):
        database = {}
        if os.path.exists(filename):
            with open(filename, "r") as file:
                for line in file:
                    parts = line.strip().split("-")
                    if len(parts) >= 3:
                        rfid, name, absen = parts[0], parts[1], parts[2]
                        foto = parts[3] if len(parts) == 4 else ""
                        database[rfid] = {"name": name, "absen": absen, "foto": foto}
        return database

    def key_pressed(self, event):
        if event.char.isdigit():
            self.rfid_code += event.char
        elif event.keysym == "Return":
            self.show_data()

    def show_data(self):
        if not self.rfid_code:
            return
        waktu_tap = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        mode = self.mode.get()
        self.code_label.config(text=f"Kode RFID: {self.rfid_code}")
        if self.rfid_code in self.database:
            data = self.database[self.rfid_code]
            self.name_label.config(text=f"Nama: {data['name']}")
            self.absen_label.config(text=f"No Absen: {data['absen']}")
            self.time_label.config(text=f"{mode} pada: {waktu_tap}")
            if data['foto'] and os.path.exists(data['foto']):
                img = Image.open(data['foto']).resize((100, 120))
                self.foto_img = ImageTk.PhotoImage(img)
                self.photo_label.config(image=self.foto_img)
            else:
                self.photo_label.config(image="")
            if not self.check_duplicate(self.rfid_code, waktu_tap.split(" ")[0], mode):
                with open(self.log_filename, "a", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow([self.rfid_code, data['name'], data['absen'], mode, waktu_tap])
                self.listbox.insert(tk.END, f"{waktu_tap} - {data['name']} ({mode})")
        else:
            self.name_label.config(text="Data tidak ditemukan.")
            self.absen_label.config(text="")
            self.time_label.config(text=f"{mode} pada: {waktu_tap}")
            self.photo_label.config(image="")
            with open(self.log_filename, "a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([self.rfid_code, "Tidak Dikenal", "", mode, waktu_tap])
            self.listbox.insert(tk.END, f"{waktu_tap} - Tidak Dikenal ({mode})")
        self.update_stats()
        self.root.after(5000, self.reset_display)
        self.rfid_code = ""

    def check_duplicate(self, rfid, tanggal, mode):
        with open(self.log_filename, "r") as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                if row[0] == rfid and row[3] == mode and row[4].startswith(tanggal):
                    return True
        return False

    def reset_display(self):
        self.rfid_code = ""
        self.code_label.config(text="")
        self.name_label.config(text="")
        self.absen_label.config(text="")
        self.time_label.config(text="")
        self.photo_label.config(image="")
        self.root.focus_set()

    def export_laporan(self):
        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if filename:
            with open(self.log_filename, "r") as src, open(filename, "w", newline="") as dst:
                dst.write(src.read())
            messagebox.showinfo("Sukses", f"Laporan berhasil disimpan ke {filename}")

    def load_today_log(self):
        today = datetime.now().strftime("%Y-%m-%d")
        with open(self.log_filename, "r") as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                if row[4].startswith(today):
                    self.listbox.insert(tk.END, f"{row[4]} - {row[1]} ({row[3]})")
        self.update_stats()

    def update_stats(self):
        self.total_label.config(text=f"Total Tap: {self.listbox.size()}")

if __name__ == "__main__":
    root = tk.Tk()
    app = RFIDReaderApp(root)
    root.mainloop()
