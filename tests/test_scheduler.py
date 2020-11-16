import time
from pimetrics.scheduler import Scheduler


class Probe:
    def __init__(self):
        self.count = 0

    def run(self):
        self.count += 1


def test_scheduler():
    scheduler = Scheduler()
    scheduler.run(once=True)
    scheduler.register(Probe(), 2)
    scheduler.register(Probe(), 3)
    scheduler.register(Probe(), 5)
    scheduler.register(Probe(), 10)
    assert len(scheduler.scheduled_items) == 4
    scheduler.run(once=True)
    assert scheduler.scheduled_items[0].probe.count == 1
    assert scheduler.scheduled_items[1].probe.count == 1
    assert scheduler.scheduled_items[2].probe.count == 1
    assert scheduler.scheduled_items[3].probe.count == 1
    before = time.time()
    scheduler.run(duration=7)
    assert time.time() - before >= 7
    assert scheduler.scheduled_items[0].probe.count == 5
    assert scheduler.scheduled_items[1].probe.count == 3
    assert scheduler.scheduled_items[2].probe.count == 2
    assert scheduler.scheduled_items[3].probe.count == 1
    scheduler.run(once=True)
    assert scheduler.scheduled_items[0].probe.count == 6
    assert scheduler.scheduled_items[1].probe.count == 4
    assert scheduler.scheduled_items[2].probe.count == 3
    assert scheduler.scheduled_items[3].probe.count == 2
