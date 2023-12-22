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
                        if "Neuer Atemzug" in data:
                            SettingsSection.breathingCounter += 1
                            print("Breathing Counter erhöht:", SettingsSection.breathingCounter)
                        # Hier kannst du je nach empfangenen Daten Aktionen in deiner GUI auslösen
                except serial.SerialException:
                    print("Fehler beim Lesen der seriellen Schnittstelle")


        self.settings_label = customtkinter.CTkLabel(frame, text="EINSTELLUNGEN")
        self.settings_label.grid(row=1, column=0, pady=10, padx=10, sticky="w")

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
    


class ScrollbarSection:
    tk_textbox = None
    def __init__(self, frame):

        self.scrollbar_section_label = customtkinter.CTkLabel(frame, text="STATUS REPORT")
        self.scrollbar_section_label.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        self.update_button = customtkinter.CTkButton(frame, text="Update", command=self.update)
        self.update_button.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        self.tk_textbox = customtkinter.CTkTextbox(frame, state="disabled", height=340, width=400, fg_color="black")
        self.tk_textbox.grid(row=3, column=1, padx=10, pady=10, sticky="nsew")

    def update(self):
        print("update")
        SettingsSection.ser.write(b'U') 

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
            formatted_message = f"\n{current_datetime}: {cleaned_message}\n"

            print(f"Debug: formatted message: {repr(formatted_message)}")

            cls.tk_textbox.insert(tk.END, formatted_message)
            cls.tk_textbox.see(tk.END)
            cls.tk_textbox.configure(state=tk.DISABLED)




class ControlSection:
    def __init__(self, frame):
        self.controlling_label = customtkinter.CTkLabel(master=frame, text="CONTROLLING")
        self.controlling_label.grid(row=1, column=0, pady=10, padx=10, sticky="w")

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

    def pause_action(self):
        print("pause")
        SettingsSection.ser.write(b'pause') 
        

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
        self.volume_label = customtkinter.CTkLabel(frame, text="Atemvolumen", text_color="grey")
        self.volume_label.grid(row=9, column=0, columnspan=2, padx=10, sticky="w")

        self.volume_slider = customtkinter.CTkSlider(
            frame,
            to=800,
            from_=0,
            number_of_steps=800,
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
        self.breathing_label = customtkinter.CTkLabel(master=frame, text="ATEMMUSTER")
        self.breathing_label.grid(row=1, column=0, pady=10, padx=10, sticky="w")

        self.breathing_patterns = ["Standard", "Apnoe", "Hypopnoe", "Cheyne-Stokes-Atmung"]  # Beispieloptionen
        self.selected_breathing_pattern = customtkinter.StringVar()

        self.breathing_dropdown = customtkinter.CTkOptionMenu(
            frame,
            width=200,
            variable=self.selected_breathing_pattern,
            values=self.breathing_patterns
        )
        self.breathing_dropdown.grid(row=2, column=0, padx=10, pady=10, sticky="w")

        self.apply_breathing_button = customtkinter.CTkButton(frame, text="Anwenden", command=self.apply_breathing)
        self.apply_breathing_button.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        self.placeholder = customtkinter.CTkLabel(frame, text="")
        self.placeholder.grid(row=3, pady=10)

        self.data_button = customtkinter.CTkButton(frame, text="Datei auswählen", command=self.choose_data)
        self.data_button.grid(row=4, column=0, pady=10, padx=10, sticky="w")
        
        self.upload_button = customtkinter.CTkButton(frame, text="Hochladen", command=self.upload_data, state="normal")
        self.upload_button.grid(row=6, column=0, pady=10, padx=10)

        self.upload_label = customtkinter.CTkLabel(frame, text="Aktuelle Datei:")
        self.upload_label.grid(row=5, column=0, columnspan=2, pady=10, padx=10, sticky="w")

        self.uploaded_file_label = customtkinter.CTkLabel(frame, text="", font=("", 12))
        self.uploaded_file_label.grid(row=5, column=1, pady=10, padx=10, sticky="w")

        self.play_data_label = customtkinter.CTkButton(frame, text="Abspielen", command=self.play_data)
        self.play_data_label.grid(row=6, column=1, pady=10, padx=10)

    def apply_breathing(self):
        selected_pattern = self.breathing_dropdown.get()
        print(f"Applying Breathing Pattern: {selected_pattern}")
        if selected_pattern == "Standard":
            self.apply_standard()
        elif selected_pattern == "Apnoe":
            #message = f"Eine Apnoe von 10 Sekunden wird auf dem Lungensimulator abgespielt"
            #ScrollbarSection.update_text(message)
            self.apply_apnoe()
        elif selected_pattern == "Hypopnoe":
            #message = f"Eine Hypopnoe wird auf dem Lungensimulator abgespielt"
            #ScrollbarSection.update_text(message)
            self.apply_hypopnoe()
        elif selected_pattern == "Cheyne-Stokes-Atmung":
            ScrollbarSection.update_text("Die Cheyne-Stokes-Atmung wird abgespielt.")
            self.apply_cheyne_stokes()

    def apply_standard(self):
        SettingsSection.ser.write(b"select-2")

    def apply_apnoe(self):
        print("apnoe läuft")
        SettingsSection.ser.write(b"vol-500")
        time.sleep(0.1)
        SettingsSection.ser.write(b"freq-13")
        time.sleep(10)
        print("10 sekunden um")
        SettingsSection.ser.write(b"vol-0")
        time.sleep(10)
        SettingsSection.ser.write(b"freq-20")
        time.sleep(0.1)
        SettingsSection.ser.write(b"vol-600")
        time.sleep(1)
        SettingsSection.ser.write(b"freq-13")


    def apply_hypopnoe(self):
        print("hypopnoe öäuft")
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

    def apply_cheyne_stokes(self):
        print("Cheyne-Stokes läuft")

        SettingsSection.ser.write(b"vol-550")
        time.sleep(0.1)
        SettingsSection.ser.write(b"freq-13")

        for volume in range(600, -200, -100):
            while True:
                uart_data = SettingsSection.ser.readline().decode('utf-8').strip()
                
                if uart_data == "Neuer Atemzug":
                    SettingsSection.ser.write(f"vol-{volume}".encode())
                    break  # Die While-Schleife verlassen und zum nächsten Volumen gehen
        for volume in range(0, 600, 100):
            while True:
                uart_data = SettingsSection.ser.readline().decode('utf-8').strip()
                
                if uart_data == "Neuer Atemzug":
                    SettingsSection.ser.write(f"vol-{volume}".encode())
                    break  
        ScrollbarSection.update_text("Die Cheyne-Stokes-Atmung ist beendet.")


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
        except Exception as e:
            print(f"Fehler beim Verarbeiten der CSV-Datei: {str(e)}")

    def upload_data(self):
        try:
            SettingsSection.ser.write(b"feed")
            time.sleep(0.1)
            data_line = "" + "".join(map(str, self.output_data)) + "!"
            print(type(data_line))
            SettingsSection.ser.write(data_line.strip().encode())
            self.upload_update_button_state("disabled")
        except Exception as e:
            ScrollbarSection.update_text("Datei konnte nicht hochgeladen werden.")

    def play_data(self):
        SettingsSection.ser.write(b"select-1")

    def upload_update_button_state(self, states):
        self.upload_button.configure(state = states)




