import sys
import tkinter as tk
from multiprocessing import Process
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
from pathlib import Path
from tkinter import ttk
import threading
import queue
import datetime
import time
from PIL import Image, ImageTk
from itertools import count
from threading_impl.Thread_Pool import Thread_Pool
import gc
import concurrent.futures
from machine_learning.stock_analysis_prediction import main as analyze_stock
from machine_learning.stock_analysis_prediction import get_preview_prices
from tkinter import StringVar
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class GUI(Thread_Pool):

    # Initialize necessary data for GUI
    def __init__(self):
        super().__init__(amount_of_threads=1)
        self.path = Path(os.getcwd()).parent.absolute()
        self.job_queue = queue.Queue()
        self.cache_queue = queue.Queue()
        self.threads = []
        self.load_thread:threading.Thread = None
        self.img=None
        self.image=None
        
        self.window = tk.Tk(screenName='Stock Analysis')
        self.window.attributes('-fullscreen', True)
        w, h = self.window.winfo_screenwidth(), self.window.winfo_screenheight()
        self.window.geometry("%dx%d+0+0" % (w, h))

        self.content = ttk.Frame(self.window,width=100,height=100)
        self.boolean1 = tk.BooleanVar()
        self.force_bool = tk.BooleanVar()

        self.watchlist = []
        self.quick_select= StringVar(self.content)
        self.quick_select.set('SPY') # default value
        self.stock_input = tk.Entry(self.content)
        self.quick_select.trace('w',self.quick_gen)
        self.generate_button = ttk.Button(self.content, text="Generate",command= self.generate_callback)
        # self.output_image = tk.Canvas(self.window,width=1400,height=1400,bg='white')
        self.load_layout = tk.Canvas(self.content,width=100,height=100,bg='white')

        self.window.bind('<Return>',self.generate_callback)
        self.window.bind('<F5>',self.dropdown_callback)
        s = ttk.Style(self.window)
        self.page_loc = 1 # Map page number to location
        try: # if image exists, don't recreate
            self.buttonImage.size 
        except:
            self.buttonImage = Image.open(f'{self.path}/data/icons/next.png')
            self.buttonPhoto = ImageTk.PhotoImage(self.buttonImage)
            self.buttonImage2 = Image.open(f'{self.path}/data/icons/previous.png')
            self.buttonPhoto2 = ImageTk.PhotoImage(self.buttonImage2)
            self.next_page_button = ttk.Button(self.content, padding='10 10 10 10',image=self.buttonPhoto,text="",command= lambda: self.job_queue.put(threading.Thread(target=self.analysis_page,args=())))
            self.next_page_button.grid(column=4, row=20)
            self.previous_page_button = ttk.Button(self.content, padding='10 10 10 10',image=self.buttonPhoto2,text="",command= lambda: self.job_queue.put(threading.Thread(target=self.predict_page,args=())))
            self.previous_page_button.grid(column=2, row=20)

        # self.output_image.pack(expand='yes',side='right')
        self.background_tasks_label = tk.Label(self.content,text=f'Currently pre-loading a few stocks, this may take a bit...')
        self.load_image = Image.open(f'{self.path}/data/icons/load.gif')
        self.exited = False
        self.frames = []
        self.loc = 0
        self.lock = threading.Lock()
        self.is_retrieving = True
        s.configure('.', background='white')
    
    def dropdown_callback(self,event=None):
        if isinstance(event, tk.Event):
            self.cache_queue.put(threading.Thread(target=self.load_dropdown,args=(type(event),)))
    """
        Loads the dropdown bar with current prices for all stocks located under 'default.csv'.
    """
    def load_dropdown(self,event=None):
        self.watchlist_file = open(f'{self.path}/data/watchlist/default.csv','r')
        lines = self.watchlist_file.readlines()
        self.watchlist = []
        for line in lines:
            try:
                ticker=line[0:line.find(",")].strip().upper()
            except:
                ticker=line.strip().upper()
            if event is not None:
                pnl_percent=get_preview_prices(ticker,force_generation=True)
            else:
                pnl_percent=get_preview_prices(ticker,force_generation=False)
            self.watchlist.append(f'{ticker}     {pnl_percent[0]}     {pnl_percent[1]}')
        
        # destroy object before proceeding
        try:
            self.stock_dropdown.destroy()
        except:
            pass

        self.stock_dropdown = tk.OptionMenu(self.content,self.quick_select,*self.watchlist)
        self.stock_dropdown.grid(column=4,row=0)
        self.watchlist_file.close()

    def quick_gen(self,event,*args,**vargs):
        self.stock_input.delete(0,tk.END)
        self.stock_input.insert(0,self.quick_select.get().split(' ')[0])
        self.generate_callback(event)
        
    def generate_callback(self,event=None):
        if self.page_loc == 1:
            self.job_queue.put(threading.Thread(target=self.load_model,args=(self.stock_input.get(),self.boolean1.get(),False,self.force_bool.get())))
        elif self.page_loc == 2:
            self.job_queue.put(threading.Thread(target=self.analyze_model,args=(self.stock_input.get(),self.boolean1.get(),False,self.force_bool.get())))
    
    """Analyze stock through charting"""
    def analyze_model(self,ticker,has_actuals,is_not_closed,is_caching=False,force_generation=False):
        if self.page_loc == 2:# Analyze page
            self.background_tasks_label.config(text=f'Currently loading {ticker}, this may take a bit...')
            if not is_caching:
                self.generate_button.grid_forget()
            if not has_actuals:
                dates = (datetime.date.utcnow() - datetime.timedelta(days = 75), datetime.date.utcnow() + datetime.timedelta(days = 1)) #month worth of data
            elif has_actuals:
                dates = (datetime.date.utcnow() - datetime.timedelta(days = 75), datetime.date.utcnow()) #month worth of data
            self.img=analyze_stock(ticker, has_actuals,force_generate=force_generation)[0]
            # self.image = ImageTk.PhotoImage(self.img)
            
            gc.collect()
            # time.sleep(5)
            self.dates = dates
            # print(self.dates)
            # self.output_image.delete('all')
            # self.output_image.pack(side='top')
            try:
                self.canvas.get_tk_widget().destroy()
            except:
                pass
            self.canvas = FigureCanvasTkAgg(self.img,master=self.window)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(side='bottom', fill='both', expand=1)
            # self.output_image.create_image(800,500,image=self.image)
            # self.output_image.pack(side='bottom')
            self.background_tasks_label.config(text=f'Currently pre-loading a few stocks, this may take a bit...')
            # self.generate_button.grid(column=3, row=2)
        self.stock_input.focus_set()
        self.stock_input.select_range(0, tk.END)
        return 0
    """Load a Analysis/Predict model for predicting values"""
    def load_model(self,ticker,has_actuals=False,is_caching=False,force_generation=False):
        if self.page_loc == 1: # Prediction page only...
            # self.output_image.delete('all')
            self.background_tasks_label.config(text=f'Currently loading {ticker}, this may take a bit...')
            if not is_caching:
                self.generate_button.grid_forget()
            # When predicting next day, set day to +1
            if not has_actuals:
                dates = (datetime.datetime.utcnow().date() - datetime.timedelta(days = 75), datetime.datetime.utcnow().date()+ datetime.timedelta(days = 1)) #month worth of data
            else:
                dates = (datetime.datetime.utcnow().date() - datetime.timedelta(days = 75), datetime.datetime.utcnow().date()) #month worth of data
            if not has_actuals:
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    thread = executor.submit(analyze_stock,ticker, has_actuals,force_generation)                    
            else:
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    thread = executor.submit(analyze_stock,ticker, has_actuals,force_generation)
                    
            self.img=thread.result()[0]
            # self.image = ImageTk.PhotoImage(self.img)

            gc.collect()
            self.dates = dates
            # print(self.dates)
            # self.output_image.create_image(600,500,image=self.image)
            # self.output_image.pack(side='bottom')
            try:
                self.canvas.get_tk_widget().destroy()
            except:
                pass
            self.canvas = FigureCanvasTkAgg(self.img,master=self.window)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(side='bottom', fill='both', expand=1)
            for idx,thread in enumerate(self.threads):
                self.threads.pop(idx)
            self.background_tasks_label.config(text=f'Currently pre-loading a few stocks, this may take a bit...')
            # self.generate_button.grid(column=3, row=2)
        self.stock_input.focus_set()
        self.stock_input.select_range(0, tk.END)
        return 0
    
    """Set view to new window to make sure user wants to quit"""
    def on_closing(self):
        self.exited = True
        self.stop_threads=True
        self.is_retrieving = False
        self.content.destroy()
        self.window.destroy()
        exit(0)
        


    def next_frame(self):
        # new_im = ImageTk.PhotoImage(self.load_image.copy())
        for frame in self.frames:            
            if self.is_retrieving:
                self.obj = self.load_layout.create_image(50,50,image=frame)
                time.sleep(1)
                self.load_layout.delete(self.obj)
            else:
                return
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
            self.generate_button.grid_remove()
            self.generate_button = ttk.Button(self.content, text="Analyze",command= self.generate_callback)
            # self.output_image.delete('all')

    """ Swap to Predict page """            
    def predict_page(self):
        if self.page_loc == 2:#Analysis page
            self.page_loc = 1
            self.generate_button.grid_remove()
            self.generate_button = ttk.Button(self.content, text="Generate",command= self.generate_callback)
            # self.output_image.delete('all')
        
    """ Manages GUI-side.  Button actions map to functions"""
    def run(self):
        self.content.pack(side='top')
        self.load_layout.grid(column=3,row=9)
        self.stock_label = tk.Label(self.content,text="Stock:")
        self.stock_label.grid(column=2,row=0)
        self.stock_input.insert(0,'SPY')
        self.stock_input.grid(column=3,row=0)
        self.boolean1 = tk.BooleanVar()
        self.boolean1.set(False)

        self.force_bool = tk.BooleanVar()
        self.force_bool.set(False)
        self.force_refresh = ttk.Checkbutton(self.content, text="Force Regeneration", variable=self.force_bool)
        self.force_refresh.grid(column=2, row=2)
        self.has_actuals = ttk.Checkbutton(self.content, text="Compare Predicted", variable=self.boolean1)
        self.has_actuals.grid(column=4, row=1)
        self.generate_button = ttk.Button(self.content, text="Generate",command= self.generate_callback)
        self.generate_button.grid(column=3, row=2)
        # self.next_page_button.pack(side='bottom')
        self.cache_queue.put(threading.Thread(target=self.load_dropdown,args=()))
        # self.cache_queue.put(threading.Thread(target=self.load_model,args=('SPY',False,False,True,False)))
        # self.cache_queue.put(threading.Thread(target=self.load_model,args=('TSLA',False,False,True,False)))
        # self.cache_queue.put(threading.Thread(target=self.load_model,args=('KO',False,False,True,False)))
        # self.cache_queue.put(threading.Thread(target=self.load_model,args=('COIN',False,False,True,False)))
        # self.cache_queue.put(threading.Thread(target=self.load_model,args=('RBLX',False,False,True,False)))
        # self.cache_queue.put(threading.Thread(target=self.load_model,args=('NOC',False,False,True,False)))
        # self.cache_queue.put(threading.Thread(target=self.load_model,args=('DASH',False,False,True,False)))
        # self.cache_queue.put(threading.Thread(target=self.load_model,args=('ABNB',False,False,True,False)))
        # self.cache_queue.put(threading.Thread(target=self.load_model,args=('SNOW',False,False,True,False)))
        # self.cache_queue.put(threading.Thread(target=self.load_model,args=('XLU',False,False,True,False)))
        # self.cache_queue.put(threading.Thread(target=self.load_model,args=('SNOW',False,False,True,False)))
        # self.cache_queue.put(threading.Thread(target=self.load_model,args=('UPS',False,False,True,False)))
        # self.cache_queue.put(threading.Thread(target=self.load_model,args=('ULTA',False,False,True,False)))
        self.window.protocol("WM_DELETE_WINDOW", lambda : self.on_closing())

        self.window.mainloop()
    def exit_check(self):
        while True:
            if self.exited:
                raise ChildProcessError('[INFO] Application Signal End.')         
            else:
                time.sleep(2)  
    """ Constant loop that checks for tasks to-be completed.  Manages Computations"""
    def task_loop(self):
        exit_thread = threading.Thread(target=self.exit_check)
        exit_thread.daemon = True
        exit_thread.start()
        while True:
            if self.exited:
                raise ChildProcessError('[INFO] Application Signal End.')         
            self.obj = None 
            # Queue for when the generate button is submitted and any other button actions go here
            while self.job_queue.qsize() > 0:
                self.is_retrieving = True
                if self.load_thread is None:
                    self.load_thread = threading.Thread(target=self.start_loading)
                    self.load_thread.start()
                self.generate_button.grid_forget()
                tmp_thread = self.job_queue.get()
                try:
                    if self.start_worker(tmp_thread) == 0:
                        if self.job_queue.qsize() > 0:
                            pass
                        else:
                            break
                    else:
                        # pass
                        self.job_queue.put(tmp_thread)
                        self.join_workers()
                except: #Already started the thread, ignore, add back to queue
                    pass
            
            # Queue for begin caching on stocks
            while self.cache_queue.qsize() > 0:
                self.is_retrieving = True
                if self.load_thread is None:
                    self.load_thread = threading.Thread(target=self.start_loading)
                    self.load_thread.start()
                self.background_tasks_label.grid(column=3,row=6)
                # self.generate_button.grid_forget()
                tmp_thread = self.cache_queue.get()
                try:
                    if self.start_worker(tmp_thread) == 0:
                        if self.cache_queue.qsize() > 0:
                            pass
                        else:
                            break
                    else:
                        self.cache_queue.put(tmp_thread)
                        self.join_workers()
                except Exception as e: # Already started the thread, just add back, ignoring error
                    print(str(e))
                    pass

                            
            
            # Reset Screen to original state
            try:
                try:
                    sys.stdout = open(os.devnull, 'w')
                    self.join_workers()
                    gc.collect()
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
    t = threading.Thread(target=ui.task_loop)
    t.daemon=True
    t.start()
    ui.run()
    
    