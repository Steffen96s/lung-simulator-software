import customtkinter
import serial
from serial.tools.list_ports import comports
import tkinter as tk
from tkinter import scrolledtext
from datetime import datetime
import customtkinter
from tkinter import filedialog
import os
import time
from tkinter import *
import csv
import threading
import serial


class SettingsSection:
    ser = None
    breathingCounter = 0
    def __init__(self, frame):

        def serial_read_thread():
            while True:
                try:
                    # Nur lesen, wenn die Verbindung hergestellt wurde
                    if SettingsSection.ser:
                        data = SettingsSection.ser.readline().decode('utf-8')
                        print("Empfangene daten: ", (data))
                        ScrollbarSection.update_text(data)
                        SettingsSection.update_last_uart_data(data)
                        # if "Neuer Atemzug" in data:
                        #     #SettingsSection.breathingCounter += 1
                        #     print("Breathing Counter erhöht:", SettingsSection.breathingCounter)

                except serial.SerialException:
                    print("Fehler beim Lesen der seriellen Schnittstelle")

        self.settings_label = customtkinter.CTkLabel(frame, text="EINSTELLUNGEN")
        self.settings_label.grid(row=1, column=0, pady=5, padx=10, sticky="w")

        # Initialisiere das Dropdown-Menü mit vorhandenen COM-Ports
        self.update_com_ports()
        self.selected_com_port = customtkinter.StringVar()

        self.com_ports_dropdown = customtkinter.CTkOptionMenu(
            master=frame,
            variable=self.selected_com_port,
            values=self.com_port_options,
            dynamic_resizing=False,
        )
        self.com_ports_dropdown.grid(row=2, column=0, padx=10, pady=10)

        self.setting_button = customtkinter.CTkButton(master=frame, text="Verbinden", command=self.connect)
        self.setting_button.grid(row=2, column=1, padx=10)

        self.placeholdder = customtkinter.CTkLabel(frame, text="", width=100)
        self.placeholdder.grid(row=2, column=2)

        self.serial_thread = threading.Thread(target=serial_read_thread, daemon=True)
        self.serial_thread.start()


    def update_com_ports(self):
        # Aktualisiere die Liste der COM-Ports
        self.com_port_options = [port.device for port in comports()]

    def connect(self):
        selected_port = self.selected_com_port.get()
        if selected_port:
            try:
                # Verbindung herstellen mit dem ausgewählten COM-Port (selected_port)
                SettingsSection.ser = serial.Serial(selected_port, 460800)
                print(f"Connected to {selected_port}")
                success_message = f"Verbindung hergestellt mit {selected_port}"
                ScrollbarSection.update_text(success_message)

                # Hier kannst du weitere Aktionen mit der ser-Verbindung durchführen
            except serial.SerialException as e:
                print(f"Error connecting to {selected_port}: {e}")
                error_message = f"Fehler bei der Verbindung zu {selected_port}: {e}"
                ScrollbarSection.update_text(error_message)

    @classmethod
    def update_last_uart_data(cls, data):
        if "Neuer Atemzug" in data:
            cls.last_uart_data = data
            cls.breathingCounter += 1
            print("Breathing Counter erhöht:", cls.breathingCounter)

    @classmethod
    def get_last_uart_data(cls):
        return cls.breathingCounter
    
class ScrollbarSection:
    tk_textbox = None
    def __init__(self, frame):

        self.scrollbar_section_label = customtkinter.CTkLabel(frame, text="STATUS")
        self.scrollbar_section_label.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        self.tk_textbox = customtkinter.CTkTextbox(frame, state="disabled", height=435, width=400, fg_color="black")
        self.tk_textbox.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")


    @classmethod
    def update_text(cls, message):
        def remove_null_bytes(input_str):
            return input_str.replace('\x00', '')
        if cls.tk_textbox is not None:
            cls.tk_textbox.configure(state=tk.NORMAL)

            print(f"Debug: message type: {type(message)}, value: {repr(message)}")

            # Entferne Escape-Zeichen
            cleaned_message = remove_null_bytes(message)

            current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if "Neuer Atemzug " not in cleaned_message:
                formatted_message = f"\n{current_datetime}: {cleaned_message}\n"
                print(f"Debug: formatted message: {repr(formatted_message)}")
                cls.tk_textbox.insert(tk.END, formatted_message)
                cls.tk_textbox.see(tk.END)

        cls.tk_textbox.configure(state=tk.DISABLED)

class ControlSection:
    def __init__(self, frame):
        self.controlling_label = customtkinter.CTkLabel(master=frame, text="STEUERUNG")
        self.controlling_label.grid(row=1, column=0, pady=5, padx=10, sticky="w")

        self.start_button = customtkinter.CTkButton(master=frame, text="Start", command=self.start_action)
        self.start_button.grid(row=2, column=0, padx=10, pady=10)

        self.pause_button = customtkinter.CTkButton(master=frame, text="Stop", command=self.pause_action)
        self.pause_button.grid(row=2, column=1, padx=10, pady=10)

        self.placeholder = customtkinter.CTkLabel(frame, text="")
        self.placeholder.grid(row=2, column=3, padx=30)

        self.create_frequency_widgets(frame)
        self.create_volume_widgets(frame)

    def start_action(self):
        print("start")
        SettingsSection.ser.write(b'breathe')
        BreathingPatternSection.button_start_state = True

    def pause_action(self):
        print("pause")
        SettingsSection.ser.write(b'pause') 
        BreathingPatternSection.button_start_state = False
        

    def create_frequency_widgets(self, frame):
        self.frequency_label = customtkinter.CTkLabel(frame, text="Atemfrequenz", text_color="grey")
        self.frequency_label.grid(row=6, column=0, columnspan=2, padx=10, sticky="w")

        self.frequency_slider = customtkinter.CTkSlider(
            frame,
            to=35,
            from_=6,
            command=self.frequency_slider_changed,
            number_of_steps=29
        )
        self.frequency_slider.grid(row=7, columnspan=3, pady=10, sticky="w", padx=8)

        self.current_value_label = customtkinter.CTkLabel(frame, text="", font=("", 16))
        self.current_value_label.grid(row=7, column=1, padx=20, sticky="e")

        self.frequency_apply_button = customtkinter.CTkButton(frame, text="Frequenz anwenden", command=self.apply_frequency, font=("",12), height=24)
        self.frequency_apply_button.grid(row=8, column=0, padx=10, pady=10, sticky="w")

    def frequency_slider_changed(self, value):
        self.current_value_label.configure(text=f"{value} bpm")
        print("Frequency changed")

    def apply_frequency(self):
        value = int(self.frequency_slider.get())
        print("Wert an Microcontroller senden: ", value)
        SettingsSection.ser.write(f"freq-{value}".encode()) 

    def create_volume_widgets(self, frame):
        max_volume = 800
        self.volume_label = customtkinter.CTkLabel(frame, text="Atemvolumen", text_color="grey")
        self.volume_label.grid(row=9, column=0, columnspan=2, padx=10, sticky="w")

        self.volume_slider = customtkinter.CTkSlider(
            frame,
            to=int(max_volume * 0.92),
            from_=0,
            number_of_steps=int(max_volume * 0.92),
            command=self.volume_slider_changed,
        )
        self.volume_slider.grid(row=10, columnspan=2, pady=10, sticky="w", padx=8)

        self.current_volume_label = customtkinter.CTkLabel(frame, text="", font=("", 16))
        self.current_volume_label.grid(row=10, column=1, padx=20, sticky="e")

        self.volume_apply_button = customtkinter.CTkButton(frame, text="Volumen anwenden", command=self.apply_volume, font=("",12), height=24)
        self.volume_apply_button.grid(row=11, column=0, padx=10, pady=10, sticky="w")

    def volume_slider_changed(self, value):
        self.current_volume_label.configure(text=f"{value} ml")
        print("Volume changed")

    def apply_volume(self):
        value = int(self.volume_slider.get())
        print("Wert an Microcontroller senden: ", value)
        SettingsSection.ser.write(f"vol-{value}".encode())

class BreathingPatternSection:
    def __init__(self, frame):
        self.processed_data = []
        self.volumes = [600, 500, 400, 300, 200, 100, 0, 100, 200, 300, 400, 500, 600]

        self.breathing_label = customtkinter.CTkLabel(master=frame, text="SIMULATION")
        self.breathing_label.grid(row=1, column=0, pady=5, padx=10, sticky="w")

        self.placeholder_label1 = customtkinter.CTkLabel(frame, text="Atemmuster", text_color="grey")
        self.placeholder_label1.grid(row=2, padx=10, sticky="w")

        self.breathing_patterns = ["Standard", "Apnoe", "Hypopnoe", "Cheyne-Stokes-Atmung"]  # Beispieloptionen
        self.selected_breathing_pattern = customtkinter.StringVar()

        self.breathing_dropdown = customtkinter.CTkOptionMenu(
            frame,
            width=200,
            variable=self.selected_breathing_pattern,
            values=self.breathing_patterns
        )
        self.breathing_dropdown.grid(row=3, column=0, padx=10, pady=10, sticky="w")

        self.apply_breathing_button = customtkinter.CTkButton(frame, text="Anwenden", command=self.apply_breathing)
        self.apply_breathing_button.grid(row=3, column=1, padx=10, pady=10, sticky="w")

        self.placeholder_label2 = customtkinter.CTkLabel(frame, text="Datenimport", text_color="grey")
        self.placeholder_label2.grid(row=4, padx=10, sticky="w")

        self.data_button = customtkinter.CTkButton(frame, text="Datei auswählen", command=self.choose_data)
        self.data_button.grid(row=5, column=0, pady=10, padx=10, sticky="w")
        
        self.upload_button = customtkinter.CTkButton(frame, text="Hochladen", command=self.upload_data, state="disabled")
        self.upload_button.grid(row=5, column=1, pady=10, padx=10)

        self.upload_label = customtkinter.CTkLabel(frame, text="Aktuelle Datei: Aktuell noch keine Datei vorhanden.", text_color="#F5F5F5")
        self.upload_label.grid(row=6, column=0, columnspan=2, pady=5, padx=10, sticky="w")

        self.play_data_button = customtkinter.CTkButton(frame, text="Datei abspielen", command=self.play_data, state= "disabled")
        self.play_data_button.grid(row=7, column=0, pady=10, padx=10, sticky="w")

    def apply_breathing(self):
        selected_pattern = self.breathing_dropdown.get()
        print(f"Applying Breathing Pattern: {selected_pattern}")
        if selected_pattern == "Standard":
            self.apply_standard()
        elif selected_pattern == "Apnoe":
            self.apply_apnoe()
        elif selected_pattern == "Hypopnoe":
            self.apply_hypopnoe()
        elif selected_pattern == "Cheyne-Stokes-Atmung":
            self.apply_cheyne_stokes(self.volumes)

    def apply_standard(self):
        SettingsSection.ser.write(b"select-2")

    def run_apnoe(self):
        print("apnoe läuft")
        SettingsSection.ser.write(b"vol-500")
        time.sleep(0.1)
        SettingsSection.ser.write(b"freq-13")
        time.sleep(10)
        print("10 sekunden um")
        SettingsSection.ser.write(b"vol-0")
        time.sleep(10)
        print("10 sekunden um")
        SettingsSection.ser.write(b"freq-20")
        time.sleep(0.1)
        SettingsSection.ser.write(b"vol-600")
        time.sleep(1)
        SettingsSection.ser.write(b"freq-13")

    def start_apnoe_thread(self):
        apnoe_thread = threading.Thread(target=self.run_apnoe)
        apnoe_thread.start()

    # Rufe diese Funktion auf, um die Apnoe in einem separaten Thread zu starten
    def apply_apnoe(self):
        self.start_apnoe_thread()
        ScrollbarSection.update_text("Eine Apnoe von 10 Sekunden wird auf dem Lungensimulator abgespielt")


    def apply_hypopnoe(self):
        print("hypopnoe läuft")
        SettingsSection.ser.write(b"vol-500")
        time.sleep(0.1)
        SettingsSection.ser.write(b"freq-13")
        time.sleep(10)
        print("10 sekunden um")
        SettingsSection.ser.write(b"vol-200")
        time.sleep(10)
        SettingsSection.ser.write(b"freq-13")
        time.sleep(0.1)
        SettingsSection.ser.write(b"vol-500")

    def apply_cheyne_stokes(self, volume_list):
        print("Cheyne-Stokes läuft")

        SettingsSection.ser.write(b"vol-550")
        time.sleep(0.1)
        SettingsSection.ser.write(b"freq-13")

        def check_breath_and_update_volume(index, last_counter):
            current_counter = SettingsSection.breathingCounter

            if current_counter > last_counter:
                SettingsSection.ser.write(f"vol-{volume_list[index]}".encode())
                if index + 1 < len(volume_list):
                    # Verzögerte Ausführung durch threading.Timer
                    threading.Timer(0.1, check_breath_and_update_volume, (index + 1, current_counter)).start()
                else:
                    ScrollbarSection.update_text("Die Cheyne-Stokes-Atmung ist beendet.")
            else:
                # Warte 100 Millisekunden und rufe die Funktion erneut auf
                threading.Timer(0.1, check_breath_and_update_volume, (index, last_counter)).start()

        # Starte den Timer für die asynchrone Ausführung der Funktion
        threading.Timer(1.0, check_breath_and_update_volume, (0, SettingsSection.breathingCounter)).start()


    def choose_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.upload_label.configure(text=file_path)
            if file_path:
                file_name = os.path.basename(file_path)
                self.upload_label.configure(text=f"Aktuelle Datei: {file_name}")
                if file_path:
                    self.process_csv(file_path)
    
    def process_csv(self, file_path):
        try:
            self.output_data= []
            with open(file_path, 'r') as file:
                reader = csv.reader(file, delimiter=';')
                for row in reader:
                    processed_row = ';'.join([f'{float(value):.2f}'.replace(',', '.') for value in row])
                    self.processed_data.append(processed_row)  # Hinzufügen der verarbeiteten Zeile zur Liste
                    print(f"Processed Row: {processed_row}")

                # Zusätzliches: Daten gemäß den Anforderungen ausgeben
                self.output_data = ';'.join(self.processed_data)
                print(f"Output Data: {self.output_data}!")
            self.upload_button.configure(state="normal")
        except Exception as e:
            print(f"Fehler beim Verarbeiten der CSV-Datei: {str(e)}")
            ScrollbarSection.update_text("Fehler beim Verarbeiten der CSV-Datei")

    def upload_data(self):
        try:
            SettingsSection.ser.write(b"feed")
            time.sleep(0.1)
            data_line = "" + "".join(map(str, self.output_data)) + "!"
            print(type(data_line))
            SettingsSection.ser.write(data_line.strip().encode())
            self.play_data_button.configure(state="normal")
        except Exception as e:
            ScrollbarSection.update_text(f"Fehler beim Hochladen der CSV-Datei: {str(e)}")

    def play_data(self):
        SettingsSection.ser.write(b"select-1")






