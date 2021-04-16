import schedule
import time

from actions import DailyPCRPositivityRateAction, PandemicICUBedsCompletenessAction

daily_PCR_positivity_rate_action = PandemicICUBedsCompletenessAction()


def start_scheduler():
    schedule.every(10).seconds.do(daily_PCR_positivity_rate_action.execute)

    print("start scheduler")
    while True:
        schedule.run_pending()
        time.sleep(1)


start_scheduler()