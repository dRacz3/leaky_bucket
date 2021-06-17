import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

from threading import Thread, Lock

import time


class LeakyBucket:
  """
  Naive implementation of a leaky bucket that can be used as a rate limiter.
  """
    def __init__(self, limit: int, regen_rate_per_sec: int):
        self.limit = limit
        self.tokens = limit
        self.regen_rate_per_sec = regen_rate_per_sec
        self.mutex = Lock()
        self.regen_interval = 0.1
        self.running = False
        self.regeneration_thread = None

    def start_regeneration(self):
        if self.regeneration_thread is None:
            self.regeneration_thread = Thread(target=self._regeneration)
            self.regeneration_thread.start()
        else:
            logging.info('Regeneration thread already running!')

    def stop_regeneration(self):
        self.running = False

    def _regeneration(self):
        self.running = True
        while self.running:
            self.mutex.acquire()
            tokens_to_regenerate_in_one_iteration = self.regen_rate_per_sec * self.regen_interval
            logging.debug(f'Regenerating {tokens_to_regenerate_in_one_iteration} tokens..')
            self.tokens += tokens_to_regenerate_in_one_iteration
            if self.tokens > self.limit:
                logging.debug('Bucket already full')
                self.tokens = self.limit
            self.mutex.release()
            time.sleep(self.regen_interval)
        self.regeneration_thread = None

    def consume_one(self):
        while True:
            if self.tokens >= 1:
                break
            logging.debug('Waiting for a token...')
            time.sleep(0.01)
        self.mutex.acquire()
        self.tokens -= 1
        self.mutex.release()


if __name__ == '__main__':
    bucket = LeakyBucket(3, 1)
    bucket.start_regeneration()
    
    
    for i in range(10):
        bucket.consume_one()
        logging.info(f'[{i}] - Doing the thing')
    print('Done!')
    bucket.stop_regeneration()
