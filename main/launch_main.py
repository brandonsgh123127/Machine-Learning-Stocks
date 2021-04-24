import sys
import subprocess
# import machine_learning.stock_analysis_prediction as sp
import tkinter as tk
import os
from pathlib import Path
from tkinter import ttk


path = Path(os.getcwd()).parent.absolute()
def load_model(ticker,has_actuals,is_not_closed):
    output = str(subprocess.check_output(["python", f'{path}/machine_learning/stock_analysis_prediction.py', f'{ticker}', f'{has_actuals}', f'{is_not_closed}'], shell=False).decode("utf-8"))
    dates = output.split()
    img = tk.PhotoImage(file=f'{path}/data/stock_no_tweets/{ticker}/{dates[0]}--{dates[1]}_predict.png')
    return img
def main():
    window = tk.Tk()
    title_frame = tk.LabelFrame(window,text="Welcome to Stock Predictor!",width=900,height=900)
    title_frame.pack(fill='both',expand='yes')
    title = tk.Label(title_frame,text="Machine learning based prediction model that utilizes regression prediction models.")
    subtitle = tk.Label(title_frame,text="Model produces output that contains:\n\
                                             predicted Open differences from past day\n\
                                             predicted Close differences from past day\n\
                                             derivative difference between both days\n\
                                             and other useful EMA predictions by utilizing the 14 and 30 EMA.")
    title.pack()
    subtitle.pack()
    
    content = ttk.Frame(window)
    content.pack()
    is_not_closed = ttk.Checkbutton(content, text="Predict ongoing day?", variable=True, onvalue=True)

    has_actuals = ttk.Checkbutton(content, text="Compare Model to Last Close?", variable=True, onvalue=True)
    has_actuals.grid(column=0, row=0)
    generate_button = ttk.Button(content, text="Generate")
    generate_button.grid(column=0, row=1)
    # generate_button.pack()
    
    output_image = tk.Canvas(window,width=1080,height=900)
    img = load_model('SPY', has_actuals=has_actuals, is_not_closed=False)
    output_image.create_image(640,480,anchor='s',image=img)
    output_image.pack()
    
    window.mainloop()
if __name__ == '__main__':
    main()