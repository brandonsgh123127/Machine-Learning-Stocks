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
import time
from PIL import Image, ImageTk
from itertools import count

class GUI():
    def __init__(self):
        self.path = Path(os.getcwd()).parent.absolute()
        self.window = tk.Tk(screenName='Stock Analysis')
        self.content = ttk.Frame(self.window,width=400,height=400)
        self.output_image = tk.Canvas(self.window,width=1920,height=600)
        self.output_image.pack(expand='yes', fill='both',side='right')
        self.background_tasks_label = tk.Label(self.content,text="Currently Pre-loading some stocks, this may take a bit...")
        self.job_queue = queue.Queue()
        self.cache_queue = queue.Queue()
        self.load_image = Image.open(f'{self.path}/data/icons/load.gif')
        self.exited = False
        self.frames = []
        self.loc = 0
        self.lock = threading.Lock()
        self.is_retrieving = True

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
            self.exited = True
            exit(0)
        else:
            self.__init__()
            self.run()
    def next_frame(self):
        # new_im = ImageTk.PhotoImage(self.load_image.copy())
        for frame in self.frames:
            
            self.obj = self.output_image.create_image(400,400,image=frame)
            time.sleep(0.2)
            self.output_image.delete(self.obj)
        # time.sleep(0.1)
        # self.output_image.delete(obj)

    def start_loading(self):
        try:
            for i in count(1):
                with self.lock:
                    self.load_image.seek(i)
                    self.frames.append(ImageTk.PhotoImage(self.load_image.copy()))
        except:
            pass
        while self.is_retrieving:
            self.next_frame()
                    

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
            
            self.content.pack()
            self.stock_label = tk.Label(self.content,text="Stock:")
            self.stock_label.grid(column=2,row=0)
            self.stock_input = tk.Entry(self.content)
            self.stock_input.insert(0,'SPY')
            self.stock_input.grid(column=3,row=0)
            self.boolean1 = tk.BooleanVar()
            self.boolean1.set(False)
            self.boolean2 = tk.BooleanVar()
            self.boolean2.set(False)
            self.is_not_closed = ttk.Checkbutton(self.content, text="Predict Tomorrow During Trade Day?", variable=self.boolean1,command= lambda: self.job_queue.put(threading.Thread(target=self.get_current_price)))
            self.is_not_closed.grid(column=2, row=1)
            self.has_actuals = ttk.Checkbutton(self.content, text="Don't predict Future(Compare Model with last close)", variable=self.boolean2)
            self.has_actuals.grid(column=4, row=1)
            self.generate_button = ttk.Button(self.content, text="Generate",command= lambda: self.job_queue.put(threading.Thread(target=self.load_model,args=(self.stock_input.get(),self.boolean2.get(),self.boolean1.get()))))
            self.generate_button.grid(column=3, row=2)
            self.cache_queue.put(threading.Thread(target=self.load_model,args=('SPY',False,False,True)))
            self.cache_queue.put(threading.Thread(target=self.load_model,args=('NVDA',False,False,True)))
            self.cache_queue.put(threading.Thread(target=self.load_model,args=('TSLA',False,False,True)))
            self.cache_queue.put(threading.Thread(target=self.load_model,args=('KO',False,False,True)))
            self.cache_queue.put(threading.Thread(target=self.load_model,args=('COIN',False,False,True)))
            self.cache_queue.put(threading.Thread(target=self.load_model,args=('RBLX',False,False,True)))
            self.cache_queue.put(threading.Thread(target=self.load_model,args=('NOC',False,False,True)))
            self.cache_queue.put(threading.Thread(target=self.load_model,args=('LMT',False,False,True)))
            self.cache_queue.put(threading.Thread(target=self.load_model,args=('PEP',False,False,True)))
            self.cache_queue.put(threading.Thread(target=self.load_model,args=('FB',False,False,True)))
            self.cache_queue.put(threading.Thread(target=self.load_model,args=('GOOGL',False,False,True)))
            self.cache_queue.put(threading.Thread(target=self.load_model,args=('DASH',False,False,True)))
            self.cache_queue.put(threading.Thread(target=self.load_model,args=('GOOG',False,False,True)))
            self.cache_queue.put(threading.Thread(target=self.load_model,args=('AMC',False,False,True)))
            self.window.mainloop()
            self.window.protocol("WM_DELETE_WINDOW", self.on_closing())
    def task_loop(self):
        while True:
            _kill_event = threading.Event()
            item_queue = []
            self.obj = None
            self.load_thread:threading.Thread = threading.Thread()
            while self.job_queue.qsize() > 0:
                self.is_retrieving = True
                self.load_thread = threading.Thread(target=self.start_loading)
                self.load_thread.start()

                item_queue.append(self.job_queue.get(0))
                item_queue[-1].start()
            while self.cache_queue.qsize() > 0:
                self.is_retrieving = True
                self.load_thread = threading.Thread(target=self.start_loading)
                self.load_thread.start()

                self.background_tasks_label.grid(column=3,row=6)
                self.generate_button.grid_forget()
                item_queue.append(self.cache_queue.get(0))
                item_queue[-1].start()
            while len(item_queue) > 0:
                item_queue[-1].join()
                item_queue.pop()
            try:
                self.is_retrieving=False

                self.background_tasks_label.grid_forget()
                self.generate_button.grid(column=3, row=2)
            except:
                pass
            if self.exited:
                exit(0)
                    
if __name__ == '__main__':
    ui = GUI()
    threading.Thread(target=ui.task_loop).start()
    ui.run()
    