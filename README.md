Lungensimulator Software
Description:

This repository contains the necessary files for utilizing the software associated with the lung simulator. The software, written in Python, is designed to control the hardware of the lung simulator through UART communication.

Features include the ability to establish a connection to the hardware, basic controls, and the simulation of predefined and custom individual files. Additionally, an example CSV file named "flattening_example" is provided for data import.

The corresponding hardware code, which operates in conjunction with the software, can be found at the following link: https://github.com/Steffen96s/lung-simulator-hardware/tree/main

HOW TO RUN:

- Open the repository in Visual Studio and install the Python programming language.
- Ensure that the corresponding modified hardware version is uploaded to the microcontroller, as only this version functions seamlessly with the software.
- Launch the software by running the main.py file.

Error Handling:

In the event of a software error, a simple hardware reset is required.

