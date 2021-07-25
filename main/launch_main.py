import sys
import subprocess
# import machine_learning.stock_analysis_prediction as sp
import tkinter as tk
import os
from pathlib import Path
from tkinter import ttk
import threading
import queue
from tkinter import messagebox
import datetime
import time
from PIL import Image, ImageTk
from itertools import count
from threading_impl.Thread_Pool import Thread_Pool

         
class GUI(Thread_Pool):
    def __init__(self):
        super().__init__(amount_of_threads=2)
        self.path = Path(os.getcwd()).parent.absolute()
        self.window = tk.Tk(screenName='Stock Analysis')
        self.content = ttk.Frame(self.window,width=100,height=100)
        self.output_image = tk.Canvas(self.window,width=1400,height=1400,bg='white')
        self.load_layout = tk.Canvas(self.content,width=200,height=200,bg='white')
        s = ttk.Style(self.window)
        self.page_loc = 1 # Map page number to location

        self.output_image.pack(expand='yes',side='right')
        self.background_tasks_label = tk.Label(self.content,text=f'Currently pre-loading a few stocks, this may take a bit...')
        self.job_queue = queue.Queue()
        self.cache_queue = queue.Queue()
        self.threads = []
        self.load_thread:threading.Thread = None
        self.load_image = Image.open(f'{self.path}/data/icons/load.gif')
        self.exited = False
        self.frames = []
        self.loc = 0
        self.lock = threading.Lock()
        self.is_retrieving = True
        self.boolean1 = False
        self.boolean2 = False
        s.configure('.', background='white')



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
    
    """Load a Analysis/Predict model for predicting values"""
    def load_model(self,ticker,has_actuals,is_not_closed,is_caching=False,force_generation=False):
        if self.page_loc == 1: # Prediction page only...
            self.background_tasks_label.config(text=f'Currently loading {ticker}, this may take a bit...')
            if not is_caching:
                self.generate_button.grid_forget()
            skippable = False
            # When predicting next day, set day to +1
            if is_not_closed:
                dates = (datetime.date.today() - datetime.timedelta(days = 50), datetime.date.today() + datetime.timedelta(days = 1)) #month worth of data
            else:
                dates = (datetime.date.today() - datetime.timedelta(days = 50), datetime.date.today() + datetime.timedelta(days = 1)) #month worth of data
            if not force_generation and (Path(f'{self.path}/data/stock_no_tweets/{ticker}/{dates[0]}--{dates[1]}_divergence.png').exists() and Path(f'{self.path}/data/stock_no_tweets/{ticker}/{dates[0]}--{dates[1]}_predict_u.png').exists() and Path(f'{self.path}/data/stock_no_tweets/{ticker}/{dates[0]}--{dates[1]}_predict.png').exists() and not has_actuals and not is_not_closed):
                skippable = True
            elif not force_generation and (Path(f'{self.path}/data/stock_no_tweets/{ticker}/{dates[0]}--{dates[1]}_divergence_a.png').exists() and Path(f'{self.path}/data/stock_no_tweets/{ticker}/{dates[0]}--{dates[1]}_predict_u_a.png').exists() and Path(f'{self.path}/data/stock_no_tweets/{ticker}/{dates[0]}--{dates[1]}_predict_a.png').exists() and has_actuals and not is_not_closed):
                skippable = True
            if not skippable:
                if is_not_closed:
                    self.threads.append(subprocess.Popen(["python", f'{self.path}/machine_learning/stock_analysis_prediction.py', 'predict', f'{ticker}', f'{has_actuals == True}', f'{True}', f'{self.open_input.get()}',f'{self.high_input.get()}',f'{self.low_input.get()}',f'{self.close_input.get()}'], shell=False))
                    time.sleep(10)
                    self.threads.append(subprocess.Popen(["python", f'{self.path}/machine_learning/stock_analysis_prediction.py', 'new', f'{ticker}', f'{has_actuals == True}', f'{True}', f'{self.open_input.get()}',f'{self.high_input.get()}',f'{self.low_input.get()}',f'{self.close_input.get()}'], shell=False))
                    time.sleep(10)
                    self.threads.append(subprocess.Popen(["python", f'{self.path}/machine_learning/stock_analysis_prediction.py', 'u', f'{ticker}', f'{has_actuals == True}', f'{True}', f'{self.open_input.get()}',f'{self.high_input.get()}',f'{self.low_input.get()}',f'{self.close_input.get()}'], shell=False))
                    time.sleep(3)
                    self.output = str(subprocess.check_output(["python", f'{self.path}/machine_learning/stock_analysis_prediction.py', 'divergence', f'{ticker}', f'{has_actuals == True}', f'{is_not_closed == True}', f'{self.open_input.get()}',f'{self.high_input.get()}',f'{self.low_input.get()}',f'{self.close_input.get()}'], shell=False).decode("utf-8"))
                else:
                    self.threads.append(subprocess.Popen(["python", f'{self.path}/machine_learning/stock_analysis_prediction.py', 'predict', f'{ticker}', f'{has_actuals == True}', f'{is_not_closed == True}'], shell=False))
                    time.sleep(10)
                    self.threads.append(subprocess.Popen(["python", f'{self.path}/machine_learning/stock_analysis_prediction.py', 'new', f'{ticker}', f'{has_actuals == True}', f'{is_not_closed == True}'], shell=False))
                    time.sleep(10)
                    self.threads.append(subprocess.Popen(["python", f'{self.path}/machine_learning/stock_analysis_prediction.py', 'u', f'{ticker}', f'{has_actuals == True}', f'{is_not_closed == True}'], shell=False))
                    time.sleep(3)
                    self.output = str(subprocess.check_output(["python", f'{self.path}/machine_learning/stock_analysis_prediction.py', 'divergence', f'{ticker}', f'{has_actuals == True}', f'{is_not_closed == True}'], shell=False).decode("utf-8"))
                for idx,thread in enumerate(self.threads):
                    thread.wait()
                    self.threads.pop(idx)
                self.dates = self.output.split()
            else:
                self.dates = dates
            # print(self.dates)
            if not is_caching:
                if not has_actuals:
                    if not is_not_closed:
                        self.img = ImageTk.PhotoImage(Image.open(f'{self.path}/data/stock_no_tweets/{ticker}/{self.dates[0]}--{self.dates[1]}_predict.png'))
                        self.img2 = ImageTk.PhotoImage(Image.open(f'{self.path}/data/stock_no_tweets/{ticker}/{self.dates[0]}--{self.dates[1]}_predict_u.png'))
                        self.img4 = ImageTk.PhotoImage(Image.open(f'{self.path}/data/stock_no_tweets/{ticker}/{self.dates[0]}--{self.dates[1]}_new.png'))
                        self.img3 = ImageTk.PhotoImage(Image.open(f'{self.path}/data/stock_no_tweets/{ticker}/{self.dates[0]}--{self.dates[1]}_divergence.png').resize((480,360),Image.ANTIALIAS))
                    else:
                        self.img = ImageTk.PhotoImage(Image.open(f'{self.path}/data/stock_no_tweets/{ticker}/{self.dates[0]}--{self.dates[1]}_predict-i.png'))
                        self.img2 = ImageTk.PhotoImage(Image.open(f'{self.path}/data/stock_no_tweets/{ticker}/{self.dates[0]}--{self.dates[1]}_predict_u-i.png'))
                        self.img4 = ImageTk.PhotoImage(Image.open(f'{self.path}/data/stock_no_tweets/{ticker}/{self.dates[0]}--{self.dates[1]}_new-i.png'))
                        self.img3 = ImageTk.PhotoImage(Image.open(f'{self.path}/data/stock_no_tweets/{ticker}/{self.dates[0]}--{self.dates[1]}_divergence-i.png').resize((480,360),Image.ANTIALIAS))
                else:
                    self.img = ImageTk.PhotoImage(Image.open(f'{self.path}/data/stock_no_tweets/{ticker}/{self.dates[0]}--{self.dates[1]}_predict_a.png'))
                    self.img2 = ImageTk.PhotoImage(Image.open(f'{self.path}/data/stock_no_tweets/{ticker}/{self.dates[0]}--{self.dates[1]}_predict_u_a.png'))
                    self.img4 = ImageTk.PhotoImage(Image.open(f'{self.path}/data/stock_no_tweets/{ticker}/{self.dates[0]}--{self.dates[1]}_new_a.png'))
                    self.img3 = ImageTk.PhotoImage(Image.open(f'{self.path}/data/stock_no_tweets/{ticker}/{self.dates[0]}--{self.dates[1]}_divergence_a.png').resize((480,360),Image.ANTIALIAS))
                self.output_image.delete('all')
                # self.output_image.pack(side='top')
                self.output_image.create_image(320,240,image=self.img2)
                
                self.output_image.create_image(960,240,image=self.img4)
        
                self.output_image.create_image(960,720,image=self.img3)
                
                self.output_image.create_image(320,720,image=self.img)
                # self.output_image.pack(side='bottom')
            for idx,thread in enumerate(self.threads):
                self.threads.pop(idx)
            self.background_tasks_label.config(text=f'Currently pre-loading a few stocks, this may take a bit...')
            # self.generate_button.grid(column=3, row=2)

        return 0
    
    """Set view to new window to make sure user wants to quit"""
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
            if self.is_retrieving:
                self.obj = self.load_layout.create_image(100,100,image=frame)
                time.sleep(0.2)
                self.load_layout.delete(self.obj)
        # time.sleep(0.1)
        # self.output_image.delete(obj)

    def start_loading(self):
        try:
            while self.is_retrieving:
                self.frames = []
                frames_loaded = False # set to true when error raised in for loop below
                if not frames_loaded:
                    try:
                        for i in count(1):
                            self.frames = [] 
                            with self.lock:
                                self.load_image.seek(i)
                                self.frames.append(ImageTk.PhotoImage(self.load_image.copy()))
                                self.next_frame()
                    except:
                        frames_loaded = True
                else:
                    self.next_frame()

            self.load_thread=None

        except:
            self.load_thread=None
            raise ChildProcessError
        
    """ Swap to Analysis page """            
    def analysis_page(self):
        if self.page_loc == 1:#Predict page
            self.page_loc = 2
            self.output_image.delete('all')

    """ Swap to Predict page """            
    def predict_page(self):
        if self.page_loc == 2:#Analysis page
            self.page_loc = 1
            self.output_image.delete('all')
        
    """ Manages GUI-side.  Button actions map to functions"""
    def run(self):
        self.content.pack(side='top')
        self.load_layout.grid(column=3,row=9)
        self.stock_label = tk.Label(self.content,text="Stock:")
        self.stock_label.grid(column=2,row=0)
        self.stock_input = tk.Entry(self.content)
        self.stock_input.insert(0,'SPY')
        self.stock_input.grid(column=3,row=0)
        self.boolean1 = tk.BooleanVar()
        self.boolean1.set(False)
        self.boolean2 = tk.BooleanVar()
        self.boolean2.set(False)
        self.force_bool = tk.BooleanVar()
        self.force_bool.set(False)
        self.is_not_closed = ttk.Checkbutton(self.content, text="Predict Next Day", variable=self.boolean2,command= lambda: self.job_queue.put(threading.Thread(target=self.get_current_price)))
        self.is_not_closed.grid(column=2, row=1)
        self.force_refresh = ttk.Checkbutton(self.content, text="Force Regeneration", variable=self.force_bool)
        self.force_refresh.grid(column=2, row=2)
        self.has_actuals = ttk.Checkbutton(self.content, text="Compare Predicted", variable=self.boolean1)
        self.has_actuals.grid(column=4, row=1)
        self.generate_button = ttk.Button(self.content, text="Generate",command= lambda: self.job_queue.put(threading.Thread(target=self.load_model,args=(self.stock_input.get(),self.boolean1.get(),self.boolean2.get(),False,self.force_bool.get()))))
        self.generate_button.grid(column=3, row=2)
        buttonImage = Image.open(f'{self.path}/data/icons/next.png')
        buttonPhoto = ImageTk.PhotoImage(buttonImage)
        self.next_page_button = ttk.Button(self.content, padding='10 10 10 10',image=buttonPhoto,text="",command= lambda: self.job_queue.put(threading.Thread(target=self.analysis_page,args=())))
        self.next_page_button.grid(column=4, row=20)
        buttonImage2 = Image.open(f'{self.path}/data/icons/previous.png')
        buttonPhoto2 = ImageTk.PhotoImage(buttonImage2)
        self.previous_page_button = ttk.Button(self.content, padding='10 10 10 10',image=buttonPhoto2,text="",command= lambda: self.job_queue.put(threading.Thread(target=self.predict_page,args=())))
        self.previous_page_button.grid(column=2, row=20)
        # self.next_page_button.pack(side='bottom')
        # self.cache_queue.put(threading.Thread(target=self.load_model,args=('SPY',False,False,True)))
        # self.cache_queue.put(threading.Thread(target=self.load_model,args=('TSLA',False,False,True)))
        # # # self.cache_queue.put(threading.Thread(target=self.load_model,args=('KO',False,False,True)))
        # self.cache_queue.put(threading.Thread(target=self.load_model,args=('COIN',False,False,True)))
        # self.cache_queue.put(threading.Thread(target=self.load_model,args=('RBLX',False,False,True)))
        # self.cache_queue.put(threading.Thread(target=self.load_model,args=('NOC',False,False,True)))
        # self.cache_queue.put(threading.Thread(target=self.load_model,args=('DASH',False,False,True)))
        # self.cache_queue.put(threading.Thread(target=self.load_model,args=('ABNB',False,False,True)))
        # self.cache_queue.put(threading.Thread(target=self.load_model,args=('SNOW',False,False,True)))
        # self.cache_queue.put(threading.Thread(target=self.load_model,args=('XLU',False,False,True)))
        # self.cache_queue.put(threading.Thread(target=self.load_model,args=('SNOW',False,False,True)))
        
        self.window.mainloop()
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing())
    """ Constant loop that checks for tasks to-be completed.  Manages Computations"""
    def task_loop(self):
        while True:
            self.obj = None
            if self.exited:
                exit(0)            
            # Queue for when the generate button is submitted and any other button actions go here
            while self.job_queue.qsize() > 0:
                self.is_retrieving = True
                if self.load_thread is None:
                    self.load_thread = threading.Thread(target=self.start_loading)
                    self.load_thread.start()
                self.generate_button.grid_forget()
                tmp_thread = self.job_queue.get(0)
                if self.start_worker(tmp_thread) != 1:
                    if self.job_queue.qsize() > 0:
                        self.job_queue.put(tmp_thread)
                        pass
                    else:
                        break
                else:
                    # pass
                    self.join_workers()
            
            # Queue for begin caching on stocks
            while self.cache_queue.qsize() > 0:
                self.is_retrieving = True
                if self.load_thread is None:
                    self.load_thread = threading.Thread(target=self.start_loading)
                    self.load_thread.start()
                self.background_tasks_label.grid(column=3,row=6)
                self.generate_button.grid_forget()
                tmp_thread = self.cache_queue.get(0)
                if self.start_worker(tmp_thread) != 1:
                    if self.cache_queue.qsize() > 0:
                        self.cache_queue.put(tmp_thread)
                        pass
                    else:
                        break
                else:
                    # pass
                    self.join_workers()

                            
            
            # Reset Screen to original state
            try:
                try:
                    sys.stdout = open(os.devnull, 'w')
                    self.join_workers()
                    sys.stdout = sys.__stdout__
                except:
                    sys.stdout = sys.__stdout__
                    pass
                if self.is_empty() and len(self.threads) == 0: 
                    self.is_retrieving=False
                    self.background_tasks_label.grid_forget()
                    self.generate_button.grid(column=3, row=2)
                else:
                    if not self.is_retrieving:
                        self.background_tasks_label.grid(column=3,row=6)
                        self.generate_button.grid_forget()
                        self.is_retrieving=True
            except:
                pass
   
if __name__ == '__main__':
    ui = GUI()
    threading.Thread(target=ui.task_loop).start()
    ui.run()
    