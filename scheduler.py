import schedule
import time

from actions import DailyPCRPositivityRateAction, PandemicICUBedsCompletenessAction

daily_PCR_positivity_rate_action = DailyPCRPositivityRateAction()
pandemic_ICU_beds_completeness_action = PandemicICUBedsCompletenessAction()


def start_scheduler():
    schedule.every().day.at("10:00").do(daily_PCR_positivity_rate_action.execute)
    schedule.every().day.at("10:00").do(pandemic_ICU_beds_completeness_action.execute)

    print("start scheduler")
    while True:
        schedule.run_pending()
        time.sleep(1)


start_scheduler()