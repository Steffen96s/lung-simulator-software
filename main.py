import customtkinter
from settings_section import SettingsSection
from settings_section import ControlSection
from settings_section import ScrollbarSection
from settings_section import BreathingPatternSection
import threading
import serial
#from settings_section import ScrollbarSection
#from control_section import ControlSection
#from scrollbar_section import ScrollbarSection
#from breathing_pattern_section import BreathingPatternSection

def create_main_gui():

    customtkinter.set_appearance_mode("dark")
    customtkinter.set_default_color_theme("dark-blue")

    root = customtkinter.CTk()
    root.title("Lungensimulator Software")
    root.resizable(False, False)

    # Create the main frame
    main_frame = customtkinter.CTkFrame(master=root)
    main_frame.pack(fill="both", expand=False)

    # Create left and right frames within the main frame
    left_frame = customtkinter.CTkFrame(master=main_frame, fg_color="SystemTransparent")
    left_frame.pack(fill="both", expand=False, side="left")

    right_frame = customtkinter.CTkFrame(master=main_frame, fg_color="SystemTransparent")
    right_frame.pack(fill="both", expand=False, side="right")

    settings_section_frame = customtkinter.CTkFrame(left_frame, fg_color="#333333")
    settings_section_frame.grid(row=1, column=0, padx=10, pady=10, sticky="w")
    settings_section = SettingsSection(settings_section_frame)

    control_section_frame = customtkinter.CTkFrame(right_frame, fg_color="#333333")
    control_section_frame.grid(row=1, column=0, padx=10, pady=10)
    control_section = ControlSection(control_section_frame)
    ControlSection.volume_apply_button = control_section.volume_apply_button

    scrollbar_section_frame = customtkinter.CTkFrame(left_frame, fg_color="#333333")
    scrollbar_section_frame.grid(row=2, column=0, padx=10, pady=10)
    scrollbar_section = ScrollbarSection(scrollbar_section_frame)

    breathing_pattern_frame = customtkinter.CTkFrame(right_frame, fg_color="#333333")
    breathing_pattern_frame.grid(row=2, column=0, padx=10, pady=10)
    breathing_pattern_section = BreathingPatternSection(breathing_pattern_frame)
    BreathingPatternSection.upload_button = breathing_pattern_section.upload_button
    BreathingPatternSection.play_data_button = breathing_pattern_section.play_data_button

    ScrollbarSection.tk_textbox = scrollbar_section.tk_textbox
    SettingsSection.ser = settings_section.ser
    SettingsSection.breathingCounter = settings_section.breathingCounter

    return root, control_section, breathing_pattern_section

if __name__ == "__main__":
    root, control_section, breathing_pattern_section = create_main_gui()
    root.mainloop()
