# -*- coding: utf-8 -*-
"""
etl_worker.task_scheduler
-------------------------
This module implements a scheduler to execute update tasks from
`etl_worker.tasks` on set time intervals.

By default it will update experiences data every 1 minute and park
schedules every 60 minutes.

copyright: © 2019 by Erik R Berlin.
license: MIT, see LICENSE for more details.

"""

import os
import sched
import time

from etl_worker import tasks

UPDATE_FREQ_SCHEDULES = int(os.environ.get("UPDATE_FREQ_SCHEDULES", 3600))
UPDATE_FREQ_EXPERIENCES = int(os.environ.get("UPDATE_FREQ_EXPERIENCES", 60))


def experiences_task():
    """Re-schedule self before executing `tasks.update_experiences`."""

    schedule.enter(UPDATE_FREQ_EXPERIENCES, 1, experiences_task)
    tasks.update_experiences()


def park_schedules_task():
    """Re-schedule self before executing `tasks.update_schedules`."""

    schedule.enter(UPDATE_FREQ_SCHEDULES, 2, park_schedules_task)
    tasks.update_schedules()


if __name__ == "__main__":
    schedule = sched.scheduler(time.time, time.sleep)
    schedule.enter(UPDATE_FREQ_SCHEDULES, 2, park_schedules_task)
    schedule.enter(UPDATE_FREQ_EXPERIENCES, 1, experiences_task)
    schedule.run()
    tasks.update_schedules()
    tasks.update_experiences()
