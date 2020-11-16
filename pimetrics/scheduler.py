import time


class _ScheduledProbe:
    def __init__(self, probe, interval):
        self.probe = probe
        self.interval = interval
        self.next_run = None

    def should_run(self):
        return self.next_run is None or self.next_run < time.time()

    def run(self):
        self.probe.run()
        self.next_run = time.time() + self.interval


class Scheduler:
    def __init__(self):
        self.scheduled_items = []
        self.min_interval = 0

    def register(self, probe, interval=5):
        """
        Register a probe to run at a certain interval

        :param probe: probe to register
        :param interval: interval at which to run the probe
        """
        self.scheduled_items.append(_ScheduledProbe(probe, interval))
        if not self.min_interval or interval < self.min_interval:
            self.min_interval = interval

    def run(self, once=False, duration=None):
        """
        Run all registered probes

        :param once: Run all probes only once (regardless of their specified interval)
        :param duration: How long we should run all required probes
        """
        end_time = None if duration is None else time.time() + duration
        while True:
            next_run = time.time() + self.min_interval
            for item in self.scheduled_items:
                if once or item.should_run():
                    item.run()
            if once or (end_time and time.time() >= end_time):
                break
            time.sleep(next_run - time.time())
