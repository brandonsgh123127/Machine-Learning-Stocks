import sys
import os
from asyncio import AbstractEventLoop, Task
from concurrent.futures import ThreadPoolExecutor

from V1.data_generator import Display
from V1.machine_learning.model import NN_Model
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
import mttkinter.mtTkinter as tk

nest_asyncio.apply()


class GUI(Thread_Pool):

    # Initialize necessary data for GUI
    def __init__(self, loop: AbstractEventLoop):
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
        self.dis = Display()
        model_choices: list = [
            # 'relu_multilayer_l2', 'relu_2layer_0regularization', 'relu_2layer_l1l2',
            #                    'relu_1layer_l2', 'new_multi_analysis_l2', 'new_multi_analysis_2layer_0regularization',
            #                    "new_scaled_l2",'new_scaled_l2_60m','new_scaled_l2_5m',
            "new_scaled_2layer",
            'new_scaled_2layer_v2'
        ]
        nn_models = [NN_Model(item) for item in model_choices]
        for model in nn_models:
            model.create_model(is_training=False)
        self.nn_dict: dict = {
            # 'relu_multilayer_l2': nn_models[0],
            # 'relu_2layer_0regularization': nn_models[1],
            # 'relu_2layer_l1l2': nn_models[2],
            # 'relu_1layer_l2': nn_models[3],
            #      'new_multi_analysis_l2': nn_models[4],
            #      'new_multi_analysis_2layer_0regularization': nn_models[5],
            #      "new_scaled_l2": nn_models[6],
            #      'new_scaled_l2_60m': nn_models[7],
            #      'new_scaled_l2_5m': nn_models[8],
            "new_scaled_2layer": nn_models[0],
            'new_scaled_2layer_v2': nn_models[1]
        }

        self.window = tk.Tk(screenName='Stock Analysis')
        self.window.attributes('-fullscreen', False)
        w, h = self.window.winfo_screenwidth() - 10, self.window.winfo_screenheight() - 10
        self.window.geometry("%dx%d+0+0" % (w, h))

        self.content = ttk.Frame(self.window, width=300, height=200)
        self.boolean1 = tk.BooleanVar(self.window)
        self.boolean1.set(False)
        self.force_bool = tk.BooleanVar(self.window)
        self.force_bool.set(False)
        self.auto_refresh = tk.BooleanVar(self.window)
        self.auto_refresh.set(False)

        self.watchlist = []
        self.quick_select = StringVar(self.content)
        self.quick_select.set('Select Stock from Dropdown')  # default value

        self.interval_text = StringVar(self.content)
        self.interval_text.set('Daily')  # default value
        self.stock_input = tk.Entry(self.content)
        self.quick_select.trace('w', lambda event=1, event2=1, event3=1: self.job_queue.put(self.quick_gen(event)))
        self.generate_button = ttk.Button(self.content, text="Generate", command=self.generate_callback)
        # self.output_image = tk.Canvas(self.window,width=1400,height=1400,bg='white')

        self.window.bind('<Return>', lambda event=1: self.job_queue.put(self.generate_callback()))
        self.window.bind('<F5>', lambda event=1: self.job_queue.put(self.dropdown_callback()))
        self.window.bind('<F9>', lambda event=1: self.cache_queue.put(self.find_biggest_moves_callback()))
        s = ttk.Style(self.window)
        self.page_loc = 1  # Map page number to location
        # try:  # if image exists, don't recreate
        #     self.buttonImage.size
        # except:
        #     self.buttonImage = Image.open(f'{self.path}/data/icons/next.png')
        #     self.buttonPhoto = ImageTk.PhotoImage(self.buttonImage)
        #     self.buttonImage2 = Image.open(f'{self.path}/data/icons/previous.png')
        #     self.buttonPhoto2 = ImageTk.PhotoImage(self.buttonImage2)
        #     self.next_page_button = ttk.Button(self.content, padding='10 10 10 10', image=self.buttonPhoto, text="",
        #                                        command=lambda: self.job_queue.put(self.analysis_page()))
        #     self.next_page_button.grid(column=7, row=5)
        #     self.previous_page_button = ttk.Button(self.content, padding='10 10 10 10', image=self.buttonPhoto2,
        #                                            text="", command=lambda: self.job_queue.put(self.predict_page()))
        #     self.previous_page_button.grid(column=5, row=5)

        # self.output_image.pack(expand='yes',side='right')
        self.background_tasks_label = tk.Label(self.content,
                                               text=f'Currently pre-loading a few stocks, this may take a bit...')
        self.page_label = tk.Label(self.content,
                                   text=self.page_loc)
        self.page_label.grid(row=4, column=6)
        self.exited = False
        self.loc = 0
        self.lock = threading.Lock()
        self.is_retrieving = True
        s.configure('.', background='white')

    async def dropdown_callback(self, event=None):
        self.cache_queue.put(self.load_dropdown(type(event)))

        return 0

    async def find_biggest_moves_callback(self, event=None):
        await self.search_big_moves(event, self.force_bool.get(),
                                    self.boolean1.get(),
                                    0.015)
        return 0

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
                pnl_percent_task = get_preview_prices(ticker, True)
                percent_task_list.append(pnl_percent_task)
            else:
                pnl_percent_task = get_preview_prices(ticker, False)
                percent_task_list.append(pnl_percent_task)
        pnl_percent = [await task for task in percent_task_list]
        for index, val in enumerate(pnl_percent):
            self.watchlist.append(f'{ticker_queue.get()}     {val}')
        del pnl_percent, percent_task_list

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
        noted_moves = find_all_big_moves(self.nn_dict, tickers, _force_generation, _has_actuals,
                                         percent, self.interval_text.get())
        # After setting noted moves, populate self noted to str
        noted_moves = await noted_moves
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
        return 0

    async def quick_gen(self, event, *args, **vargs):
        self.stock_input.delete(0, tk.END)
        self.stock_input.insert(0, self.quick_select.get().split(' ')[0])
        await self.generate_callback(event)

    async def generate_callback(self, event=None):
        if self.page_loc == 1:
            self.job_queue.put(self.load_model(
                self.stock_input.get(), self.boolean1.get(), False, self.force_bool.get()))
        elif 2 <= self.page_loc <= 3:
            self.job_queue.put(self.load_model(
                self.stock_input.get(), self.boolean1.get(), False, self.force_bool.get()))

    async def add_fib_val(self, event=None):
        try:
            val = self.fib_opt_val_input.get()
            self.opt_fib_vals_set.add(str(val))
            self.fib_opt_val_list.insert("end", val)
        except Exception as e:
            print(f'[INFO] Failed to add fib value to listbox!\n\t{str(e)}')

    async def delete_fib_val(self, event=None):
        try:
            idx = self.fib_opt_val_list.curselection()
            val = self.fib_opt_val_list.get(idx)
            self.opt_fib_vals_set.remove(str(val))
            self.fib_opt_val_list.delete(idx)
        except Exception as e:
            print(f'[INFO] Failed to remove fib value to listbox!\n\t{str(e)}')

    """Analyze stock through charting"""

    async def image_retrieval_thread(self, loop, task):
        asyncio.set_event_loop(loop)
        await task
        self.img = task[0]
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

    async def analyze_model(self, ticker, has_actuals, is_not_closed, is_caching=False, force_generation=False,
                            opt_fib_vals=[]):
        if self.page_loc == 2:  # Analyze page
            self.background_tasks_label.config(text=f'Currently loading {ticker}, this may take a bit...')
            if not is_caching:
                self.generate_button.grid_forget()
            analyze_task = analyze_stock(self.nn_dict, ticker, has_actuals,
                                         force_generate=force_generation,
                                         opt_fib_vals=opt_fib_vals,
                                         dis=self.dis, skip_display=False,
                                         output=4)
            t = threading.Thread(target=self.image_retrieval_thread, args=(self.loop, analyze_task))
            t.daemon = True
            t.start()

    """Load a Analysis/Predict model for predicting values"""

    async def load_model(self, ticker, has_actuals=False, is_caching=False, force_generation=False):
        # self.output_image.delete('all')
        self.background_tasks_label.config(text=f'Currently loading {ticker}, this may take a bit...')
        if not is_caching:
            self.generate_button.grid_forget()
        analysis_task = await analyze_stock(self.nn_dict, ticker, has_actuals, force_generation,
                                            self.interval_text.get(), list(self.opt_fib_vals_set),
                                            dis=self.dis, skip_display=False, output=4)

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

    """ Swap to Analysis page """

    async def analysis_page(self):
        if 1 <= self.page_loc <= 2:  # Predict page
            self.page_loc = self.page_loc + 1
            self.page_label.config(text=self.page_loc)
            self.generate_button.grid_remove()
            self.generate_button = ttk.Button(self.content, text="Analyze",
                                              command=lambda event=1: self.job_queue.put(self.generate_callback()))
            # self.output_image.delete('all')

    """ Swap to Predict page """

    async def predict_page(self):
        if 1 < self.page_loc <= 3:  # Analysis page
            self.page_loc = self.page_loc - 1
            self.page_label.config(text=self.page_loc)
            self.generate_button.grid_remove()
            self.generate_button = ttk.Button(self.content, text="Generate",
                                              command=lambda event=1: self.job_queue.put(self.generate_callback()))
            # self.output_image.delete('all')

    """ Manages GUI-side.  Button actions map to functions"""

    async def run(self):
        t = threading.Thread(target=self.job_loop_in_thread, args=(self.loop,))
        t.daemon = True
        t.start()
        t = threading.Thread(target=self.cache_loop_in_thread, args=(self.loop,))
        t.daemon = True
        t.start()

        self.content.pack(side='top')
        self.stock_label = tk.Label(self.content, text="Stock:")
        self.stock_label.grid(column=2, row=0)
        self.stock_input.insert(0, 'SPY')
        self.stock_input.grid(column=3, row=0)
        self.fib_opt_val_input = tk.Entry(self.content)
        self.fib_opt_val_input.grid(column=1, row=4)
        self.fib_opt_val_add_button = ttk.Button(self.content, text="Add",
                                                 command=lambda event=1: self.job_queue.put(self.add_fib_val()))
        self.fib_opt_val_add_button.grid(column=1, row=5)
        self.fib_opt_val_remove_button = ttk.Button(self.content, text="Remove",
                                                    command=lambda event=1: self.job_queue.put(self.delete_fib_val()))
        self.fib_opt_val_remove_button.grid(column=2, row=5)
        self.fib_opt_val_list = tk.Listbox(self.content)
        self.fib_opt_val_list.grid(column=1, row=6)
        self.opt_fib_vals_set: set = {'', }
        self.opt_fib_vals_set.remove('')
        self.force_refresh = tk.Checkbutton(self.content, text="Force Regeneration", variable=self.force_bool)
        self.force_refresh.grid(column=1, row=2)
        self.auto_refresh_checkbutton = tk.Checkbutton(self.content, text="AutoRefresh", variable=self.auto_refresh)
        self.auto_refresh_checkbutton.grid(column=6, row=2)
        self.has_actuals = tk.Checkbutton(self.content, text="Compare Predicted", variable=self.boolean1)
        self.has_actuals.grid(column=6, row=1)
        self.generate_button = ttk.Button(self.content, text="Generate",
                                          command=lambda event=1: self.job_queue.put(self.generate_callback()))
        self.generate_button.grid(column=1, row=5)
        # self.next_page_button.pack(side='bottom')
        self.cache_queue.put(self.load_dropdown())
        self.interval_dropdown = tk.OptionMenu(self.content, self.interval_text,
                                               *['Daily', 'Weekly', 'Monthly', 'Yearly', '5m', '15m', '30m', '60m'])
        self.interval_dropdown.grid(column=3, row=0)
        self.window.protocol("WM_DELETE_WINDOW", lambda: self.on_closing())

        self.window.mainloop()

    def exit_check(self):
        while True:
            if self.exited:
                raise ChildProcessError('[INFO] Application Signal End.')
            else:
                time.sleep(2)

    """ Constant loop that checks for tasks to-be completed.  Manages Computations"""

    def job_loop_in_thread(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.jobtask_loop())

    def cache_loop_in_thread(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.cachetask_loop())

    def auto_refresh_in_thread(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.auto_refresh_loop())

    async def jobtask_loop(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        _executor = ThreadPoolExecutor(8)
        loop.set_default_executor(_executor)
        while True:
            time.sleep(0.2)
            if self.exited:
                raise ChildProcessError('[INFO] Application Signal End.')
            self.obj = None
            load_task: Task = None

            jobs_list = []
            # Queue for when the generate button is submitted and any other button actions go here
            # if self.job_queue.qsize() > 0:
            #     self.start_loading()
            while self.job_queue.qsize() > 0:
                self.is_retrieving = True
                self.generate_button.grid_forget()
                tmp_thread = await self.job_queue.get()
                jobs_list.append(tmp_thread)
            try:
                [await job for job in jobs_list]
            except Exception as e:  # Already started the thread, ignore, add back to queue
                print(f"[INFO] Couldn't gather async job tasking from tasking loop!\nException:\n\t{e}")

            # Reset Screen to original state
            try:
                try:
                    gc.collect()
                except:
                    pass
                if self.job_queue.empty():
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

    async def cachetask_loop(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        _executor = ThreadPoolExecutor(8)
        loop.set_default_executor(_executor)
        while True:
            time.sleep(0.2)
            if self.exited:
                raise ChildProcessError('[INFO] Application Signal End.')
            self.obj = None
            load_task: Task = None

            cached_list = []
            # if self.job_queue.qsize() > 0:
            #     self.start_loading()
            # Queue for begin caching on stocks
            while self.cache_queue.qsize() > 0:
                self.is_retrieving = True
                self.background_tasks_label.grid(column=3, row=6)
                # self.generate_button.grid_forget()
                tmp_thread = await self.cache_queue.get()
                cached_list.append(tmp_thread)
            try:
                # self.start_loading()
                [await item for item in cached_list]
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
                if self.cache_queue.empty():
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

    async def auto_refresh_loop(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        while True:
            if self.exited:
                raise ChildProcessError('[INFO] Application Signal End.')
            while self.auto_refresh.get() is True:
                await self.load_model(self.stock_input.get(), self.boolean1.get(),
                                      force_generation=self.force_bool.get())
                time.sleep(30)
            time.sleep(1)


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    ui = GUI(loop)
    task1 = loop.create_task(ui.run())
    loop.run_forever()
    run_task = loop.run_until_complete(task1)
    ui.auto_refresh_in_thread(loop)