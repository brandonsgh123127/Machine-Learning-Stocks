import sys
import tkinter as tk
import os
from asyncio import AbstractEventLoop, Task
from concurrent.futures import ThreadPoolExecutor

from V1.machine_learning.neural_network import Network

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
from pathlib import Path
from tkinter import ttk
import threading
import queue
import time
from PIL import Image, ImageTk
from itertools import count
from V1.threading_impl.Thread_Pool import Thread_Pool
import gc
import concurrent.futures
from V1.machine_learning.stock_analysis_prediction import main as analyze_stock
from V1.machine_learning.stock_analysis_prediction import find_all_big_moves
from V1.machine_learning.stock_analysis_prediction import get_preview_prices
from tkinter import StringVar
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import asyncio
import nest_asyncio
nest_asyncio.apply()

class GUI(Thread_Pool):

    # Initialize necessary data for GUI
    def __init__(self, loop: AbstractEventLoop ):
        super().__init__(amount_of_threads=1)
        self.loop = loop
        self._executor = ThreadPoolExecutor(8)
        self.loop.set_default_executor(self._executor)
        self.noted_dropdown = None
        self.noted_str = []
        self.obj = None
        self.force_refresh = None
        self.watchlist_file = None
        self.stock_label = None
        self.canvas = None
        self.stop_threads = False
        self.path = Path(os.getcwd()).absolute()
        self.job_queue = queue.Queue()
        self.cache_queue = queue.Queue()
        self.threads = []
        self.img = None
        self.image = None
        neural_net = Network(0, 0)
        names: list = ['relu_1layer_l2', 'relu_2layer_0regularization', 'relu_2layer_l1l2', 'relu_2layer_l1l2']
        nn_list: list = [neural_net.load_model(name=name) for name in names]
        self.nn_dict: dict = {'relu_1layer_l2': nn_list[0],
                         'relu_2layer_0regularization': nn_list[1],
                         'relu_2layer_l1l2': nn_list[2],
                         'relu_2layer_l1l2': nn_list[3]}


        self.window = tk.Tk(screenName='Stock Analysis')
        self.window.attributes('-fullscreen', False)
        w, h = self.window.winfo_screenwidth()-10, self.window.winfo_screenheight()-10
        self.window.geometry("%dx%d+0+0" % (w, h))

        self.content = ttk.Frame(self.window, width=300, height=200)
        self.boolean1 = tk.BooleanVar()
        self.force_bool = tk.BooleanVar()

        self.watchlist = []
        self.quick_select = StringVar(self.content)
        self.quick_select.set('Select Stock from Dropdown')  # default value

        self.interval_text = StringVar(self.content)
        self.interval_text.set('Daily')  # default value
        self.stock_input = tk.Entry(self.content)
        self.quick_select.trace('w', self.quick_gen)
        self.generate_button = ttk.Button(self.content, text="Generate", command=self.generate_callback)
        # self.output_image = tk.Canvas(self.window,width=1400,height=1400,bg='white')
        self.load_layout = tk.Canvas(self.content, width=100, height=100, bg='white')

        self.window.bind('<Return>', lambda event=1: self.loop.run_until_complete(self.generate_callback()))
        self.window.bind('<F5>', lambda event=1: self.loop.run_until_complete(self.dropdown_callback()))
        self.window.bind('<F9>', lambda event=1: self.loop.run_until_complete(self.find_biggest_moves_callback()))
        s = ttk.Style(self.window)
        self.page_loc = 1  # Map page number to location
        try:  # if image exists, don't recreate
            self.buttonImage.size
        except:
            self.buttonImage = Image.open(f'{self.path}/data/icons/next.png')
            self.buttonPhoto = ImageTk.PhotoImage(self.buttonImage)
            self.buttonImage2 = Image.open(f'{self.path}/data/icons/previous.png')
            self.buttonPhoto2 = ImageTk.PhotoImage(self.buttonImage2)
            self.next_page_button = ttk.Button(self.content, padding='10 10 10 10', image=self.buttonPhoto, text="",
                                               command=lambda: self.job_queue.put(self.analysis_page()))
            self.next_page_button.grid(column=4, row=20)
            self.previous_page_button = ttk.Button(self.content, padding='10 10 10 10', image=self.buttonPhoto2,
                                                   text="", command=lambda: self.job_queue.put(self.predict_page()))
            self.previous_page_button.grid(column=2, row=20)

        # self.output_image.pack(expand='yes',side='right')
        self.background_tasks_label = tk.Label(self.content,
                                               text=f'Currently pre-loading a few stocks, this may take a bit...')
        self.load_image = Image.open(f'{self.path}/data/icons/load.gif')
        self.exited = False
        self.frames = []
        self.loc = 0
        self.lock = threading.Lock()
        self.is_retrieving = True
        s.configure('.', background='white')


    async def dropdown_callback(self, event=None):
        if isinstance(event, tk.Event):
            self.cache_queue.put(self.load_dropdown(type(event)))

    async def find_biggest_moves_callback(self, event=None):
        if isinstance(event, tk.Event):
            self.cache_queue.put(self.search_big_moves(type(event), self.force_bool.get(),
                                                                 self.boolean1.get(),
                                                                 0.015))

    """
        Loads the dropdown bar with current prices for all stocks located under 'default.csv'.
    """

    async def load_dropdown(self, event=None):
        self.watchlist_file = open(f'{self.path}/data/watchlist/default.csv', 'r')
        lines = self.watchlist_file.readlines()
        self.watchlist = []
        ticker_queue: queue.SimpleQueue = queue.SimpleQueue()
        percent_task_list = []
        for line in lines:
            try:
                ticker = line[0:line.find(",")].strip().upper()
                ticker_queue.put(ticker)
            except:
                ticker = line.strip().upper()
            if event is not None:
                pnl_percent_task = self.loop.run_in_executor(self._executor,get_preview_prices,ticker, True)
                percent_task_list.append(pnl_percent_task)
            else:
                pnl_percent_task = self.loop.run_in_executor(self._executor,get_preview_prices,ticker,False)
                percent_task_list.append(pnl_percent_task)
        pnl_percent = self.loop.run_until_complete(asyncio.gather(*percent_task_list))
        for index,val in enumerate(pnl_percent):
           self.watchlist.append(f'{ticker_queue.get()}     {val}')

        # destroy object before proceeding
        try:
            self.stock_dropdown.destroy()
        except:
            pass

        self.stock_dropdown = tk.OptionMenu(self.content, self.quick_select, *self.watchlist)
        self.stock_dropdown.grid(column=5, row=0)
        self.watchlist_file.close()

    """
        Finds the biggest moves for all stocks located under 'default.csv'.
    """

    async def search_big_moves(self, event=None, _force_generation: bool = False, _has_actuals: bool = False,
                         percent: float = 0.03):

        watchlist_file = open(f'{self.path}/data/watchlist/default.csv', 'r')
        lines = watchlist_file.readlines()
        tickers = []
        self.noted_str = ['']
        for line in lines:
            try:
                ticker = line[0:line.find(",")].strip().upper()
            except:
                ticker = line.strip().upper()
            tickers.append(ticker)
        noted_moves = self.loop.run_until_complete(find_all_big_moves,self.nn_dict,tickers,_force_generation,_has_actuals,
                                         percent, self.interval_text.get())
        # After setting noted moves, populate self noted to str
        await noted_moves
        for note in noted_moves:
            self.noted_str.append(f'{note[0]} >>> {round((((note[2] + note[1]) / note[2]) - 1) * 100, 2)}%')

        # destroy object before proceeding
        try:
            self.noted_dropdown.destroy()
        except:
            pass

        self.noted_dropdown = tk.OptionMenu(self.content, self.quick_select, *self.noted_str)
        self.noted_dropdown = tk.OptionMenu(self.content, self.quick_select, *self.noted_str)
        self.noted_dropdown.grid(column=5, row=20)
        watchlist_file.close()

    async def quick_gen(self, event, *args, **vargs):
        self.stock_input.delete(0, tk.END)
        self.stock_input.insert(0, self.quick_select.get().split(' ')[0])
        await self.generate_callback(event)

    async def generate_callback(self, event=None):
        print('testing')
        if self.page_loc == 1:
            self.job_queue.put(self.load_model(
                self.stock_input.get(), self.boolean1.get(), False, self.force_bool.get()))
        elif self.page_loc == 2:
            self.job_queue.put(self.analyze_model(
                self.stock_input.get(), self.boolean1.get(), False, self.force_bool.get()))

    """Analyze stock through charting"""

    async def analyze_model(self, ticker, has_actuals, is_not_closed, is_caching=False, force_generation=False):
        if self.page_loc == 2:  # Analyze page
            self.background_tasks_label.config(text=f'Currently loading {ticker}, this may take a bit...')
            if not is_caching:
                self.generate_button.grid_forget()
            analyze_task = analyze_stock(self.nn_dict, ticker, has_actuals, force_generate=force_generation)
            await analyze_task
            self.img = analyze_task[0]
            # self.image = ImageTk.PhotoImage(self.img)

            gc.collect()
            # time.sleep(5)
            # self.output_image.delete('all')
            # self.output_image.pack(side='top')
            try:
                self.canvas.get_tk_widget().destroy()
            except:
                pass
            self.canvas = FigureCanvasTkAgg(self.img, master=self.window)
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

    async def load_model(self, ticker, has_actuals=False, is_caching=False, force_generation=False):
        if self.page_loc == 1:  # Prediction page only...
            # self.output_image.delete('all')
            self.background_tasks_label.config(text=f'Currently loading {ticker}, this may take a bit...')
            if not is_caching:
                self.generate_button.grid_forget()
            if not has_actuals:
                analysis_task = self.loop.run_until_complete(analyze_stock(self.nn_dict, ticker, has_actuals, force_generation,
                                             self.interval_text.get()))
            else:
                analysis_task = self.loop.run_until_complete(analyze_stock(self.nn_dict, ticker, has_actuals, force_generation,
                                             self.interval_text.get()))

            # analysis_res = asyncio.gather(analysis_task)
            self.img = analysis_task[0]
            # self.image = ImageTk.PhotoImage(self.img)

            gc.collect()
            # self.output_image.create_image(600,500,image=self.image)
            # self.output_image.pack(side='bottom')
            try:
                self.canvas.get_tk_widget().destroy()
            except:
                pass
            self.canvas = FigureCanvasTkAgg(self.img, master=self.window)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(side='bottom', fill='both', expand=1)
            for idx, thread in enumerate(self.threads):
                self.threads.pop(idx)
            self.background_tasks_label.config(text=f'Currently pre-loading a few stocks, this may take a bit...')
            # self.generate_button.grid(column=3, row=2)
        self.stock_input.focus_set()
        self.stock_input.select_range(0, tk.END)
        return 0

    """Set view to new window to make sure user wants to quit"""

    def on_closing(self):
        self.exited = True
        self.stop_threads = True
        self.is_retrieving = False
        self.content.destroy()
        self.window.destroy()
        exit(0)

    def next_frame(self):
        # new_im = ImageTk.PhotoImage(self.load_image.copy())
        for frame in self.frames:
            if self.is_retrieving:
                self.obj = self.load_layout.create_image(50, 50, image=frame)
                time.sleep(1)
                self.load_layout.delete(self.obj)
            else:
                return
        # time.sleep(0.1)
        # self.output_image.delete(obj)

    async def start_loading(self):
        try:
            while self.is_retrieving:
                self.frames = []
                frames_loaded = False  # set to true when error raised in for loop below
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


        except:
            raise ChildProcessError

    """ Swap to Analysis page """

    async def analysis_page(self):
        if self.page_loc == 1:  # Predict page
            self.page_loc = 2
            self.generate_button.grid_remove()
            self.generate_button = ttk.Button(self.content, text="Analyze", command=await self.generate_callback)
            # self.output_image.delete('all')

    """ Swap to Predict page """

    async def predict_page(self):
        if self.page_loc == 2:  # Analysis page
            self.page_loc = 1
            self.generate_button.grid_remove()
            self.generate_button = ttk.Button(self.content, text="Generate", command=await self.generate_callback)
            # self.output_image.delete('all')

    """ Manages GUI-side.  Button actions map to functions"""

    async def run(self):
        infinite_task_loop = self.loop.create_task(ui.task_loop())
        # t = threading.Thread(target=ui.task_loop, args=())
        # t.daemon = True
        # t.start()
        self.content.pack(side='top')
        self.load_layout.grid(column=3, row=9)
        self.stock_label = tk.Label(self.content, text="Stock:")
        self.stock_label.grid(column=2, row=0)
        self.stock_input.insert(0, 'SPY')
        self.stock_input.grid(column=3, row=0)
        self.boolean1 = tk.BooleanVar()
        self.boolean1.set(False)

        self.force_bool = tk.BooleanVar()
        self.force_bool.set(False)
        self.force_refresh = ttk.Checkbutton(self.content, text="Force Regeneration", variable=self.force_bool)
        self.force_refresh.grid(column=2, row=2)
        self.has_actuals = ttk.Checkbutton(self.content, text="Compare Predicted", variable=self.boolean1)
        self.has_actuals.grid(column=4, row=1)
        self.generate_button = ttk.Button(self.content, text="Generate", command= lambda event=1: self.loop.run_until_complete(self.generate_callback()))
        self.generate_button.grid(column=3, row=2)
        # self.next_page_button.pack(side='bottom')
        # self.cache_queue.put(await self.loop.run_in_executor(self._executor,self.load_dropdown))
        self.interval_dropdown = tk.OptionMenu(self.content, self.interval_text,
                                               *['Daily', 'Weekly', 'Monthly', 'Yearly', '5m', '15m', '30m', '1h'])
        self.interval_dropdown.grid(column=4, row=0)
        self.window.protocol("WM_DELETE_WINDOW", lambda: self.on_closing())

        self.window.mainloop()

    def exit_check(self):
        while True:
            if self.exited:
                raise ChildProcessError('[INFO] Application Signal End.')
            else:
                time.sleep(2)

    """ Constant loop that checks for tasks to-be completed.  Manages Computations"""

    async def task_loop(self):
        loop = asyncio.get_event_loop()
        asyncio.set_event_loop(loop)
        _executor = ThreadPoolExecutor(8)
        loop.set_default_executor(_executor)
        while True:
            time.sleep(2)
            if self.exited:
                raise ChildProcessError('[INFO] Application Signal End.')
            self.obj = None
            load_task: Task = None


            jobs_list=[]
            # Queue for when the generate button is submitted and any other button actions go here
            while self.job_queue.qsize() > 0:
                self.is_retrieving = True
                self.generate_button.grid_forget()
                tmp_thread = loop.run_in_executor(_executor,self.job_queue.get)
                jobs_list.append(tmp_thread)
            try:
                await asyncio.gather(*jobs_list)
                print('gathered job')
            except Exception as e:  # Already started the thread, ignore, add back to queue
                print(f"[INFO] Failed to gather async job tasking from tasking loop!\nException:\n\t{e}")

            cached_list = []
            # Queue for begin caching on stocks
            while self.cache_queue.qsize() > 0:
                self.is_retrieving = True
                self.background_tasks_label.grid(column=3, row=6)
                # self.generate_button.grid_forget()
                tmp_thread = await loop.run_in_executor(_executor,self.job_queue.get)
                cached_list.append(tmp_thread)
            try:
                await asyncio.gather(*cached_list)
                print('gathered cache job')
            except Exception as e:  # Already started the thread, just add back, ignoring error
                print(f"[INFO] Failed to gather async cached tasking from tasking loop!\nException:\n\t{e}")
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
                    self.is_retrieving = False
                    self.background_tasks_label.grid_forget()
                    self.generate_button.grid(column=3, row=2)
                else:
                    if not self.is_retrieving:
                        self.background_tasks_label.grid(column=3, row=6)
                        self.generate_button.grid_forget()
                        self.is_retrieving = True
            except:
                pass


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    ui = GUI(loop)
    task1 = asyncio.Task(ui.run())
    task_loop_task = loop.run_until_complete(task1)
    loop.run_forever()


