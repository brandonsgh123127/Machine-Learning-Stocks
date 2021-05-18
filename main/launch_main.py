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
        self.content = ttk.Frame(self.window,width=100,height=100)
        self.output_image = tk.Canvas(self.window,width=1450,height=1000)
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
        self.boolean1 = False
        self.boolean2 = False

    def get_current_price(self):
        if self.boolean2.get() == True:
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
        if Path(f'{self.path}/data/stock_no_tweets/{ticker}/{dates[0]}--{dates[1]}_divergence.png').exists() and Path(f'{self.path}/data/stock_no_tweets/{ticker}/{dates[0]}--{dates[1]}_predict_u.png').exists() and Path(f'{self.path}/data/stock_no_tweets/{ticker}/{dates[0]}--{dates[1]}_predict.png').exists() and not has_actuals and not is_not_closed:
            skippable = True
        elif Path(f'{self.path}/data/stock_no_tweets/{ticker}/{dates[0]}--{dates[1]}_divergence_a.png').exists() and Path(f'{self.path}/data/stock_no_tweets/{ticker}/{dates[0]}--{dates[1]}_predict_u_a.png').exists() and Path(f'{self.path}/data/stock_no_tweets/{ticker}/{dates[0]}--{dates[1]}_predict_a.png').exists() and has_actuals and not is_not_closed:
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
                self.img = ImageTk.PhotoImage(Image.open(f'{self.path}/data/stock_no_tweets/{ticker}/{self.dates[0]}--{self.dates[1]}_predict.png'))
                self.img2 = ImageTk.PhotoImage(Image.open(f'{self.path}/data/stock_no_tweets/{ticker}/{self.dates[0]}--{self.dates[1]}_predict_u.png'))
                self.img3 = ImageTk.PhotoImage(Image.open(f'{self.path}/data/stock_no_tweets/{ticker}/{self.dates[0]}--{self.dates[1]}_divergence.png').resize((480,360),Image.ANTIALIAS))
            else:
                self.img = ImageTk.PhotoImage(Image.open(f'{self.path}/data/stock_no_tweets/{ticker}/{self.dates[0]}--{self.dates[1]}_predict_a.png'))
                self.img2 = ImageTk.PhotoImage(Image.open(f'{self.path}/data/stock_no_tweets/{ticker}/{self.dates[0]}--{self.dates[1]}_predict_u_a.png'))
                self.img3 = ImageTk.PhotoImage(Image.open(f'{self.path}/data/stock_no_tweets/{ticker}/{self.dates[0]}--{self.dates[1]}_divergence_a.png').resize((480,360),Image.ANTIALIAS))
                print('y')
            self.output_image.delete('all')
            # self.output_image.pack(side='top')
            self.output_image.create_image(320,240,image=self.img2)
    
            self.output_image.create_image(960,720,image=self.img3)
            
            self.output_image.create_image(320,720,image=self.img)
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
            self.frames = []
            for i in count(1):
                self.frames = [] 
                with self.lock:
                    self.load_image.seek(i)
                    self.frames.append(ImageTk.PhotoImage(self.load_image.copy()))
        except:
            pass
        while self.is_retrieving is True:
            self.next_frame()
                    

    def run(self):
        self.content.pack(side='left')
        self.stock_label = tk.Label(self.content,text="Stock:")
        self.stock_label.grid(column=2,row=0)
        self.stock_input = tk.Entry(self.content)
        self.stock_input.insert(0,'SPY')
        self.stock_input.grid(column=3,row=0)
        self.boolean1 = tk.BooleanVar()
        self.boolean1.set(False)
        self.boolean2 = tk.BooleanVar()
        self.boolean2.set(False)
        self.is_not_closed = ttk.Checkbutton(self.content, text="Predict During Trade Day?", variable=self.boolean2,command= lambda: self.job_queue.put(threading.Thread(target=self.get_current_price)))
        self.is_not_closed.grid(column=2, row=1)
        self.has_actuals = ttk.Checkbutton(self.content, text="Don't predict Future", variable=self.boolean1)
        self.has_actuals.grid(column=4, row=1)
        self.generate_button = ttk.Button(self.content, text="Generate",command= lambda: self.job_queue.put(threading.Thread(target=self.load_model,args=(self.stock_input.get(),self.boolean1.get(),self.boolean2.get()))))
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
        self.cache_queue.put(threading.Thread(target=self.load_model,args=('AMD',False,False,True)))
        self.cache_queue.put(threading.Thread(target=self.load_model,args=('C',False,False,True)))

        self.window.mainloop()
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing())
    def task_loop(self):
        while True:
            _kill_event = threading.Event()
            item_queue = []
            self.obj = None
            self.load_thread:threading.Thread = None
            
            # Queue for when the generate button is submitted and any other button actions go here
            while self.job_queue.qsize() > 0:
                self.is_retrieving = True
                self.load_thread = threading.Thread(target=self.start_loading)
                self.load_thread.start()
                item_queue.append(self.job_queue.get(0))
                item_queue[-1].start()
            
            # Queue for begin caching on stocks
            while self.cache_queue.qsize() > 0:
                self.is_retrieving = True
                self.load_thread = threading.Thread(target=self.start_loading)
                self.load_thread.start()
                self.background_tasks_label.grid(column=3,row=6)
                self.generate_button.grid_forget()
                item_queue.append(self.cache_queue.get(0))
                item_queue[-1].start()
                
            # Eventually both cache and job queue items go into item queue, make sure all execute before proceeding
            while len(item_queue) > 0:
                item_queue[-1].join()
                item_queue.pop()
            
            
            # Reset Screen to original state
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
    