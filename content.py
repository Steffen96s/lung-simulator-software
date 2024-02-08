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
import re

upload_data_check = False
file_selected = False

class SettingsSection:
    ser = None
    breathingCounter = 0

    def __init__(self, frame):
        def serial_read_thread():
            while True:
                try:
                    if SettingsSection.ser:
                        data = SettingsSection.ser.readline().decode('utf-8')
                        ScrollbarSection.update_text(data)
                        SettingsSection.update_last_uart_data(data)
                except serial.SerialException:
                    SettingsSection.update_last_uart_data("Fehler beim Lesen der seriellen Schnittstelle")

        self.settings_label = customtkinter.CTkLabel(frame, text="EINSTELLUNGEN")
        self.settings_label.grid(row=1, column=0, pady=5, padx=10, sticky="w")
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
        self.com_port_options = [port.device for port in comports()]

    def connect(self):
        selected_port = self.selected_com_port.get()
        if selected_port:
            try:
                SettingsSection.ser = serial.Serial(selected_port, 460800)
                success_message = f"Verbindung hergestellt mit {selected_port}"
                ScrollbarSection.update_text(success_message)

            except serial.SerialException as e:
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
        self.tk_textbox = customtkinter.CTkTextbox(frame, state="disabled", height=480, width=400, fg_color="black")
        self.tk_textbox.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")

    @classmethod
    def update_text(cls, message):
        def remove_null_bytes(input_str):
            return input_str.replace('\x00', '')
        if cls.tk_textbox is not None:
            cls.tk_textbox.configure(state=tk.NORMAL)
            cleaned_message = remove_null_bytes(message)
            current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if "Neuer Atemzug " not in cleaned_message:
                formatted_message = f"\n{current_datetime}: {cleaned_message}\n"
                cls.tk_textbox.insert(tk.END, formatted_message)
                cls.tk_textbox.see(tk.END)
        cls.tk_textbox.configure(state=tk.DISABLED)

class ControlSection:
    volume_apply_button = None
    frequency_apply_button = None
    global connected
    def __init__(self, frame):
        self.controlling_label = customtkinter.CTkLabel(master=frame, text="STEUERUNG")
        self.controlling_label.grid(row=1, column=0, pady=5, padx=10, sticky="w")
        self.start_button = customtkinter.CTkButton(master=frame, text="Start", command=self.start_action)
        self.start_button.grid(row=2, column=0, padx=10, pady=10)
        self.pause_button = customtkinter.CTkButton(master=frame, text="Stop", command=self.pause_action)
        self.pause_button.grid(row=2, column=1, padx=10, pady=10)
        self.placeholder = customtkinter.CTkLabel(frame, text="")
        self.placeholder.grid(row=2, column=3, padx=30)
        self.frequency_label = customtkinter.CTkLabel(frame, text="Atemfrequenz [6-25 bpm]", text_color="grey")
        self.frequency_label.grid(row=6, column=0, columnspan=2, padx=10, sticky="w")
        self.frequency_slider = customtkinter.CTkSlider(
            frame,
            to=25,
            from_=6,
            command=self.frequency_slider_changed,
            number_of_steps=19
        )
        self.frequency_slider.grid(row=7, columnspan=3, pady=10, sticky="w", padx=8)
        self.frequency_apply_button = customtkinter.CTkButton(frame, text="Frequenz anwenden", command=self.apply_frequency, font=("",12), height=24)
        self.frequency_apply_button.grid(row=8, column=0, padx=10, pady=10, sticky="w")
        self.frequency_entry = customtkinter.CTkEntry(frame, textvariable=tk.StringVar(), placeholder_text="6", width=40)
        self.frequency_entry.grid(row=7, column=1, padx=20, sticky="e")
        self.frequency_entry.configure(validate="key", validatecommand=(self.frequency_entry.register(self.validate_frequency_input), "%P"))
        self.volume_label = customtkinter.CTkLabel(frame, text="Atemvolumen [0-710 ml]", text_color="grey")
        self.volume_label.grid(row=9, column=0, columnspan=2, padx=10, sticky="w")
        max_volume = 800 
        # theoretisch laut Hardware Doku 92% des max. Volumens, praktisch aber liegt der wert bei 710 ml bevor der endschalter betätigt wird
        self.volume_slider = customtkinter.CTkSlider(
            frame,
            #to=int(max_volume * 0.92),
            to=710,
            from_=0,
            number_of_steps=int(max_volume * 0.92),
            command=self.volume_slider_changed,
        )
        self.volume_slider.grid(row=10, columnspan=2, pady=10, sticky="w", padx=8)
        self.volume_apply_button = customtkinter.CTkButton(frame, text="Volumen anwenden", command=self.apply_volume, font=("",12), height=24)
        self.volume_apply_button.grid(row=11, column=0, padx=10, pady=10, sticky="w")
        self.volume_entry = customtkinter.CTkEntry(frame, textvariable=tk.StringVar(), placeholder_text="500", width=40)
        self.volume_entry.grid(row=10, column=1, padx=20, sticky="e")
        self.volume_entry.configure(validate="key", validatecommand=(self.volume_entry.register(self.validate_volume_input), "%P"))
        self.frequency_entry.bind("<FocusOut>", self.remove_focus)
        self.frequency_entry.bind("<Return>", self.remove_focus)
        self.volume_entry.bind("<FocusOut>", self.remove_focus)
        self.volume_entry.bind("<Return>", self.remove_focus)

    def remove_focus(self, event):
        self.volume_label.focus_set()

    def validate_frequency_input(self, new_text):
        if not new_text:
            return True
        if len(new_text) > 2:
            return False
        try:
            value = int(new_text)
            if 1 <= value <= 25:
                self.frequency_slider.set(value)
                return True
            else:
                return False
        except ValueError:
            return False
        
    def validate_volume_input(self, new_text):
        if not new_text:
            return True
        if len(new_text) > 3:
            return False
        try:
            value = int(new_text)
            if 0 <= value <= 710:
                self.volume_slider.set(value)
                return True
            else:
                return False
        except ValueError:
            return False

    def start_action(self):
        global file_selected
        global upload_data_check
        print("upload data check: ", upload_data_check)
        print("file selected check: ", file_selected)
        SettingsSection.ser.write(b'breathe')
        if upload_data_check == True:
            BreathingPatternSection.play_data_button.configure(state="normal")
        if upload_data_check == False and file_selected == True:
            BreathingPatternSection.upload_button.configure(state="normal")

    def pause_action(self):
        print("pause")
        SettingsSection.ser.write(b'pause')
        BreathingPatternSection.upload_button.configure(state="disabled")

    def frequency_slider_changed(self, value):
        self.frequency_entry.delete(0, tk.END)
        self.frequency_entry.insert(0, str(int(float(value))))

    def apply_frequency(self):
        value = int(self.frequency_slider.get())
        SettingsSection.ser.write(f"freq-{value}".encode()) 

    def volume_slider_changed(self, value):
        self.volume_entry.delete(0, tk.END)
        self.volume_entry.insert(0, str(int(float(value))))

    def apply_volume(self):
        value = int(self.volume_slider.get())
        SettingsSection.ser.write(f"vol-{value}".encode())

class BreathingPatternSection:
    upload_button = None
    play_data_button = None

    def __init__(self, frame):
        self.cheyne_stokes_active = False
        self.apnoe_active = False
        self.hypopnoe_active = False
        self.processed_data = []
        self.volumes = [600, 500, 400, 300, 200, 100, 0, 0, 100, 200, 300, 400, 500, 600]
        self.apnoe_volumes = [500, 500, 0, 0, 0, 650, 650]
        self.hypopnoe_volumes = [500, 500, 400, 250, 250, 250, 400, 500]
        self.breathing_label = customtkinter.CTkLabel(master=frame, text="SIMULATION")
        self.breathing_label.grid(row=1, column=0, padx=10, sticky="w", pady=5)
        self.modi_label = customtkinter.CTkLabel(frame, text="Aktueller Atemmodus: Standard", text_color="white", fg_color="#5A5A5A", corner_radius=4, width=330, pady=5)
        self.modi_label.grid(row=2, padx=10, pady=10, sticky="ew", columnspan=2)
        self.placeholder_label1 = customtkinter.CTkLabel(frame, text="Atemmuster", text_color="grey")
        self.placeholder_label1.grid(row=3, padx=10, sticky="w")
        self.breathing_patterns = ["Standard", "Apnoe", "Hypopnoe", "Cheyne-Stokes-Atmung"]
        self.selected_breathing_pattern = customtkinter.StringVar()
        self.breathing_dropdown = customtkinter.CTkOptionMenu(
            frame,
            width=200,
            variable=self.selected_breathing_pattern,
            values=self.breathing_patterns
        )
        self.selected_breathing_pattern.set("Standard")
        self.breathing_dropdown.grid(row=4, column=0, padx=10, pady=10, sticky="w")
        self.apply_breathing_button = customtkinter.CTkButton(frame, text="Anwenden", command=self.apply_breathing, state="normal")
        self.apply_breathing_button.grid(row=4, column=1, padx=10, pady=10, sticky="w")
        self.placeholder_label2 = customtkinter.CTkLabel(frame, text="Datenimport", text_color="grey")
        self.placeholder_label2.grid(row=5, padx=10, sticky="w")
        self.data_button = customtkinter.CTkButton(frame, text="Datei auswählen", command=self.choose_data)
        self.data_button.grid(row=6, column=0, pady=10, padx=10, sticky="w")
        self.upload_button = customtkinter.CTkButton(frame, text="Hochladen", command=self.upload_data, state="disabled")
        self.upload_button.grid(row=6, column=1, pady=10, padx=10)
        self.upload_label = customtkinter.CTkLabel(frame, text="Aktuelle Datei: Aktuell noch keine Datei vorhanden",  text_color="white")
        self.upload_label.grid(row=7, column=0, columnspan=2, pady=5, padx=10, sticky="w")
        self.play_data_button = customtkinter.CTkButton(frame, text="Datei abspielen", command=self.play_data, state= "disabled")
        self.play_data_button.grid(row=8, column=0, pady=10, padx=10, sticky="w")

    def apply_breathing(self):
        selected_pattern = self.breathing_dropdown.get()
        print(f"Applying Breathing Pattern: {selected_pattern}")
        if selected_pattern == "Standard":
            self.apply_standard()
            self.modi_label.configure(text="Aktueller Atemmodus: Standard")
        elif selected_pattern == "Apnoe":
            SettingsSection.ser.write(b"freq-12")
            self.apply_apnoe(self.apnoe_volumes)
            self.modi_label.configure(text="Aktueller Atemmodus: Apnoe")
        elif selected_pattern == "Hypopnoe":
            SettingsSection.ser.write(b"freq-12")
            self.apply_hypopnoe(self.hypopnoe_volumes)
            self.modi_label.configure(text="Aktueller Atemmodus: Hypopnoe")
        elif selected_pattern == "Cheyne-Stokes-Atmung":
            SettingsSection.ser.write(b"freq-12")
            self.apply_cheyne_stokes(self.volumes)
            self.modi_label.configure(text="Aktueller Atemmodus: Cheyne-Stokes")

    def apply_standard(self):
        SettingsSection.ser.write(b"select-2")
        self.stop_cheyne_stokes()  
        self.stop_apnoe() 
        self.stop_hypopnoe()
        ScrollbarSection.update_text("Atemmuster Standard wird abgespielt") 
        ControlSection.volume_apply_button.configure(state="normal")
        ControlSection.frequency_apply_button.configure(state="normal")

    def apply_apnoe(self, volume_list_apnoe):
        if not self.apnoe_active:
            self.apnoe_active = True
            ControlSection.volume_apply_button.configure(state="disabled")
            ControlSection.frequency_apply_button.configure(state="disabled")
            self.stop_cheyne_stokes() 
            self.stop_hypopnoe() 
            ScrollbarSection.update_text("Atemmuster Apnoe wird abgespielt")
            self.stop_apnoe_event = threading.Event()
            # Starte den Thread für die automatische Wiederholung
            self.apnoe_thread = threading.Thread(target=self.check_apnoe_breath_and_update_volume, args=(volume_list_apnoe,))
            self.apnoe_thread.start()

    def check_apnoe_breath_and_update_volume(self, volume_list_apnoe):
        while not self.stop_apnoe_event.is_set():
            for volume in volume_list_apnoe:
                SettingsSection.ser.write(f"vol-{volume}".encode())
                time.sleep(0.1)
                current_counter = SettingsSection.breathingCounter
                while current_counter == SettingsSection.breathingCounter and not self.stop_apnoe_event.is_set():
                    time.sleep(0.1)

    def stop_apnoe(self):
        if self.apnoe_active:
            self.stop_apnoe_event.set()
            self.apnoe_active = False

    def apply_hypopnoe(self, volume_list_hypopnoe):
        if not self.hypopnoe_active:
            self.hypopnoe_active = True
            ControlSection.volume_apply_button.configure(state="disabled")
            ControlSection.frequency_apply_button.configure(state="disabled")
            self.stop_cheyne_stokes()
            self.stop_apnoe()  
            ScrollbarSection.update_text("Atemmuster Hypopnoe wird abgespielt")
            self.stop_hypopnoe_event = threading.Event()
            # Starte den Thread für die automatische Wiederholung
            self.hypopnoe_thread = threading.Thread(target=self.check_hypopnoe_breath_and_update_volume, args=(volume_list_hypopnoe,))
            self.hypopnoe_thread.start()

    def check_hypopnoe_breath_and_update_volume(self, volume_list_hypopnoe):
        while not self.stop_hypopnoe_event.is_set():
            for volume in volume_list_hypopnoe:
                SettingsSection.ser.write(f"vol-{volume}".encode())
                time.sleep(0.1)
                current_counter = SettingsSection.breathingCounter
                while current_counter == SettingsSection.breathingCounter and not self.stop_hypopnoe_event.is_set():
                    time.sleep(0.1)

    def stop_hypopnoe(self):
        if self.hypopnoe_active:
            self.stop_hypopnoe_event.set()
            self.hypopnoe_active = False

    def apply_cheyne_stokes(self, volume_list):
        if not self.cheyne_stokes_active:
            self.cheyne_stokes_active = True
            ControlSection.volume_apply_button.configure(state="disabled")
            ControlSection.frequency_apply_button.configure(state="disabled")
            self.stop_apnoe() 
            self.stop_hypopnoe()
            ScrollbarSection.update_text("Atemmuster Cheyne-Stokes-Atmung wird abgespielt")
            self.stop_cheyne_stokes_event = threading.Event()
            # Starte den Thread für die automatische Wiederholung
            self.cheyne_stokes_thread = threading.Thread(target=self.check_breath_and_update_volume, args=(volume_list,))
            self.cheyne_stokes_thread.start()

    def check_breath_and_update_volume(self, volume_list):
        while not self.stop_cheyne_stokes_event.is_set():
            for volume in volume_list:
                SettingsSection.ser.write(f"vol-{volume}".encode())
                time.sleep(0.1)
                current_counter = SettingsSection.breathingCounter
                while current_counter == SettingsSection.breathingCounter and not self.stop_cheyne_stokes_event.is_set():
                    time.sleep(0.1)

    def stop_cheyne_stokes(self):
        if self.cheyne_stokes_active:
            self.stop_cheyne_stokes_event.set()
            self.cheyne_stokes_active = False

    def choose_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            file_name = os.path.basename(file_path)
            self.upload_label.configure(text=f"Aktuelle Datei: {file_name}")
            self.process_csv(file_path)
    
    def process_csv(self, file_path):
        global file_selected
        try:
            self.output_data= []
            with open(file_path, 'r') as file:
                reader = csv.reader(file, delimiter=';')
                for row in reader:
                    processed_row = ';'.join([f'{float(value):.2f}'.replace(',', '.') for value in row])
                    self.processed_data.append(processed_row)
                self.output_data = ';'.join(self.processed_data)
            self.upload_button.configure(state="normal")
            file_selected = True
        except Exception as e:
            ScrollbarSection.update_text("Fehler beim Verarbeiten der CSV-Datei")

    def upload_data(self):
        global upload_data_check
        try:
            SettingsSection.ser.write(b"feed")
            time.sleep(0.1)
            data_line = "" + "".join(map(str, self.output_data)) + "!"
            print(type(data_line))
            SettingsSection.ser.write(data_line.strip().encode())
            self.play_data_button.configure(state="normal")
            self.upload_button.configure(state="disabled")
            self.data_button.configure(state="disabled")
            upload_data_check = True
        except Exception as e:
            ScrollbarSection.update_text(f"Fehler beim Hochladen der CSV-Datei: {str(e)}")

    def play_data(self):
        self.modi_label.configure(text="Aktueller Atemmodus: Dateiwiedergabe")
        SettingsSection.ser.write(b"select-1")








