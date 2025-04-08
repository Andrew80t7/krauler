import time
import functools
import logging

logger = logging.getLogger('metrics')

class TimeTracker:
    def __init__(self):
        self.times = {}
        self.start_times = {}
        
    def start(self, operation):
        self.start_times[operation] = time.time()
        
    def stop(self, operation):
        if operation in self.start_times:
            duration = time.time() - self.start_times[operation]
            if operation not in self.times:
                self.times[operation] = []
            self.times[operation].append(duration)
            logger.info(f"Операция {operation} заняла {duration:.2f} сек")
            
    def get_stats(self):
        stats = {}
        for operation, times in self.times.items():
            if times:
                stats[operation] = {
                    'total': sum(times),
                    'avg': sum(times) / len(times),
                    'min': min(times),
                    'max': max(times),
                    'count': len(times)
                }
        return stats

time_tracker = TimeTracker()

def measure_time(operation):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            time_tracker.start(operation)
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                time_tracker.stop(operation)
        return wrapper
    return decorator 