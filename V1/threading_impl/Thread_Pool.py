import threading
import queue


class Thread_Pool:
    def __init__(self, amount_of_threads: int = 4):
        self.amount_of_threads = amount_of_threads
        self.worker_queue: queue.Queue() = queue.Queue()

        # print("Thread Pool initialized...")

    def start_worker(self, action: threading.Thread):
        with threading.Lock():
            if self.worker_queue.qsize() >= self.amount_of_threads:
                return 1
            else:
                # Make sure size still remains under amount of threads
                if self.worker_queue.qsize() + 1 <= self.amount_of_threads:
                    action.start()
                    self.worker_queue.put(action)
                    # time.sleep(7)
                    return 0
        return 1

    def join_workers(self):
        while not self.is_empty():
            try:
                self.worker_queue.get().join()
            except Exception as e:
                print('[ERROR] Failed to join worker!\n', str(e), flush=True)

    def is_empty(self):
        return self.worker_queue.empty()
