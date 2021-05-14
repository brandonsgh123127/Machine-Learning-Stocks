import sys
import subprocess
# import machine_learning.stock_analysis_prediction as sp
import tkinter as tk
import os
from pathlib import Path
from tkinter import ttk
import threading
import concurrent.futures
import queue
from tkinter import messagebox
import datetime
class GUI():
    def __init__(self):
        self.path = Path(os.getcwd()).parent.absolute()
        self.window = tk.Tk(screenName='Stock Analysis')
        self.output_image = None
        self.job_queue = queue.Queue()
        self.cache_queue = queue.Queue()

    def get_current_price(self):
        if self.boolean1.get() == True:
            self.open = tk.Label(self.content,text="Open:")
            self.open.grid(column=1,row=3)
            self.open_input = tk.Entry(self.content)
            self.open_input.grid(column=2,row=3)
            self.high = tk.Label(self.content,text="High:")
            self.high.grid(column=1,row=4)
            self.high_input = tk.Entry(self.content)
            self.high_input.grid(column=2,row=4)
            self.low = tk.Label(self.content,text="Low:")
            self.low.grid(column=3,row=3)
            self.low_input = tk.Entry(self.content)
            self.low_input.grid(column=4,row=3)  
            self.close = tk.Label(self.content,text="Close:")
            self.close.grid(column=3,row=4)
            self.close_input = tk.Entry(self.content)
            self.close_input.grid(column=4,row=4)  
        else:
            self.open.grid_forget()
            self.open_input.grid_forget()
            self.high.grid_forget()
            self.high_input.grid_forget()
            self.low.grid_forget()
            self.low_input.grid_forget()
            self.close.grid_forget()
            self.close_input.grid_forget()
    def load_model(self,ticker,has_actuals,is_not_closed,is_caching=False):
        if not is_caching:
            self.generate_button.grid_forget()
        threads = []
        skippable = False
        if is_not_closed:
            dates = (datetime.date.today() - datetime.timedelta(days = 50), datetime.date.today() + datetime.timedelta(days = 1)) #month worth of data
        else:
            dates = (datetime.date.today() - datetime.timedelta(days = 50), datetime.date.today() + datetime.timedelta(days = 0)) #month worth of data
        if Path(f'{self.path}/data/stock_no_tweets/{ticker}/{dates[0]}--{dates[1]}_divergence.png').exists() and Path(f'{self.path}/data/stock_no_tweets/{ticker}/{dates[0]}--{dates[1]}_predict_u.png').exists() and Path(f'{self.path}/data/stock_no_tweets/{ticker}/{dates[0]}--{dates[1]}_predict.png').exists()and not has_actuals:
            skippable = True
        elif Path(f'{self.path}/data/stock_no_tweets/{ticker}/{dates[0]}--{dates[1]}_divergence_a.png').exists() and Path(f'{self.path}/data/stock_no_tweets/{ticker}/{dates[0]}--{dates[1]}_predict_u_a.png').exists() and Path(f'{self.path}/data/stock_no_tweets/{ticker}/{dates[0]}--{dates[1]}_predict_a.png').exists() and has_actuals:
            skippable = True
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            if not skippable:
                if is_not_closed:
                    threads.append(subprocess.Popen(["python", f'{self.path}/machine_learning/stock_analysis_prediction.py', 'predict', f'{ticker}', f'{has_actuals == True}', f'{is_not_closed == True}', f'{self.open_input.get()}',f'{self.high_input.get()}',f'{self.low_input.get()}',f'{self.close_input.get()}'], shell=False))
                    threads.append(subprocess.Popen(["python", f'{self.path}/machine_learning/stock_analysis_prediction.py', 'u', f'{ticker}', f'{has_actuals == True}', f'{is_not_closed == True}', f'{self.open_input.get()}',f'{self.high_input.get()}',f'{self.low_input.get()}',f'{self.close_input.get()}'], shell=False))
                    self.output = str(subprocess.check_output(["python", f'{self.path}/machine_learning/stock_analysis_prediction.py', 'divergence', f'{ticker}', f'{has_actuals == True}', f'{is_not_closed == True}', f'{self.open_input.get()}',f'{self.high_input.get()}',f'{self.low_input.get()}',f'{self.close_input.get()}'], shell=False).decode("utf-8"))
                else:
                    threads.append(subprocess.Popen(["python", f'{self.path}/machine_learning/stock_analysis_prediction.py', 'predict', f'{ticker}', f'{has_actuals == True}', f'{is_not_closed == True}'], shell=False))
                    threads.append(subprocess.Popen(["python", f'{self.path}/machine_learning/stock_analysis_prediction.py', 'u', f'{ticker}', f'{has_actuals == True}', f'{is_not_closed == True}'], shell=False))
                    self.output = str(subprocess.check_output(["python", f'{self.path}/machine_learning/stock_analysis_prediction.py', 'divergence', f'{ticker}', f'{has_actuals == True}', f'{is_not_closed == True}'], shell=False).decode("utf-8"))
                for thread in threads:
                    thread.wait()
                print('done')
                self.dates = self.output.split()
            else:
                print("Loaded from storage")
                self.dates = dates
            print(self.dates)
            if not is_caching:
                if not has_actuals:
                    self.img = tk.PhotoImage(file=f'{self.path}/data/stock_no_tweets/{ticker}/{self.dates[0]}--{self.dates[1]}_predict.png')
                    self.img2 = tk.PhotoImage(file=f'{self.path}/data/stock_no_tweets/{ticker}/{self.dates[0]}--{self.dates[1]}_predict_u.png')
                    self.img3 = tk.PhotoImage(file=f'{self.path}/data/stock_no_tweets/{ticker}/{self.dates[0]}--{self.dates[1]}_divergence.png')
                else:
                    self.img = tk.PhotoImage(file=f'{self.path}/data/stock_no_tweets/{ticker}/{self.dates[0]}--{self.dates[1]}_predict_a.png')
                    self.img2 = tk.PhotoImage(file=f'{self.path}/data/stock_no_tweets/{ticker}/{self.dates[0]}--{self.dates[1]}_predict_u_a.png')
                    self.img3 = tk.PhotoImage(file=f'{self.path}/data/stock_no_tweets/{ticker}/{self.dates[0]}--{self.dates[1]}_divergence_a.png')
                    print('y')
                self.output_image.delete('all')
                self.output_image.create_image(960,270,anchor='w',image=self.img)
                # self.output_image.pack(side='top')
                self.output_image.create_image(960,270,anchor='e',image=self.img2)
        
                self.output_image.create_image(960,270,anchor='ne',image=self.img3)
                # self.output_image.pack(side='bottom')
            self.generate_button.grid(column=3, row=2)
        return 0
    def on_closing(self):
        self.__init__()
        self.window.iconify()

        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            exit(0)
        else:
            self.__init__()
            self.run()

    def run(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            title_frame = tk.LabelFrame(self.window,text="Welcome to Stock Predictor!",width=900,height=900)
            title_frame.pack(fill='both',expand='yes')
            title = tk.Label(title_frame,text="Machine learning based prediction model that utilizes regression prediction models.")
            subtitle = tk.Label(title_frame,text="Model produces output that contains:\n\
                                                     predicted Open differences from past day\n\
                                                     predicted Close differences from past day\n\
                                                     derivative difference between both days\n\
                                                     and other useful EMA predictions by utilizing the 14 and 30 EMA.")
            title.pack()
            subtitle.pack()
            
            self.content = ttk.Frame(self.window,width=400,height=400)
            self.content.pack()
            self.output_image = tk.Canvas(self.window,width=1920,height=900)
            self.stock_label = tk.Label(self.content,text="Stock:")
            self.stock_label.grid(column=2,row=0)
            self.stock_input = tk.Entry(self.content)
            self.stock_input.insert(0,'SPY')
            self.stock_input.grid(column=3,row=0)
            self.boolean1 = tk.BooleanVar()
            self.boolean1.set(False)
            self.boolean2 = tk.BooleanVar()
            self.boolean2.set(False)
            self.is_not_closed = ttk.Checkbutton(self.content, text="Predict ongoing day?", variable=self.boolean1,command= lambda: self.job_queue.put(executor.submit(self.get_current_price)))
            self.is_not_closed.grid(column=2, row=1)
            self.has_actuals = ttk.Checkbutton(self.content, text="Compare Mode?", variable=self.boolean2)
            self.has_actuals.grid(column=4, row=1)
            self.output_image.pack(expand='yes', fill='both',side='right')
            self.generate_button = ttk.Button(self.content, text="Generate",command= lambda: self.job_queue.put(executor.submit(self.load_model,self.stock_input.get(),self.boolean2.get(),self.boolean1.get())))
            self.generate_button.grid(column=3, row=2)
            self.cache_queue.put(executor.submit(self.load_model,'SPY',False,False,True))
            self.cache_queue.put(executor.submit(self.load_model,'NVDA',False,False,True))
            self.cache_queue.put(executor.submit(self.load_model,'TSLA',False,False,True))
            self.cache_queue.put(executor.submit(self.load_model,'KO',False,False,True))
            self.cache_queue.put(executor.submit(self.load_model,'TSLA',False,False,True))
            self.cache_queue.put(executor.submit(self.load_model,'RBLX',False,False,True))
            self.cache_queue.put(executor.submit(self.load_model,'NOC',False,False,True))
            self.cache_queue.put(executor.submit(self.load_model,'LMT',False,False,True))
            self.cache_queue.put(executor.submit(self.load_model,'PEP',False,False,True))
            self.cache_queue.put(executor.submit(self.load_model,'FB',False,False,True))
            self.cache_queue.put(executor.submit(self.load_model,'GOOGL',False,False,True))
            self.cache_queue.put(executor.submit(self.load_model,'TSLA',False,False,True))

            self.window.mainloop()
            self.window.protocol("WM_DELETE_WINDOW", self.on_closing())

            while True:
                if not self.job_queue.empty():
                    item = self.job_queue.get(0).done()
                elif not self.cache_queue.empty():
                    item = self.cache_queue.get(0).done()
                    

if __name__ == '__main__':
    ui = GUI()
    ui.run()