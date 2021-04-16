from mongo import db
from datetime import date, datetime, timedelta


class DailyPCRPositivityRateAction:
    """
    Daily PCR positivity rate
        - Warning: Daily % of positive PCR tests 3%-6%
        - Alert: Daily % of positive PCR tests > 6%

    Checks every end of day the results of all PCR tests in the db,
    finds percentages and report them as warning or alert
    """

    def execute(self):
        print("Running DailyPCRPositivityRateAction")

        # Find all PCRs from last day
        filter = {
            "date_created": {
                "$gte": (date.today() - timedelta(days=1)).strftime("%Y-%m-%d"),
                "$lt": date.today().strftime("%Y-%m-%d"),
            }
        }
        cursor = db.pcr.find(filter)
        for doc in cursor:
            # Check the amount of positives
            report = self.process_entry(doc)
            # Save alert or warning
            db.report.insert_one(report)

    def process_entry(self, entry):
        """Returns a report with alert of warning"""
        report = dict(
            processed_at=datetime.now(),
            country=entry["country"],
            region=entry["region"],
            document=entry,
        )

        if entry["positive_percentage"] > 3 and entry["positive_percentage"] < 6:
            report["status"] = "warning"
            return report
        else:
            report["status"] = "alert"
            return report


class PandemicICUBedsCompletenessAction:
    """
    Pandemic ICU beds completeness
        - Warning: 41%-60% Pandemic ICU beds completness
        - Alert: Over 61% Pandemic ICU beds completeness

    Checks the last entry of available beds in db and report a warning or alert
    """

    def execute(self):
        print("Running PandemicICUBedsCompletenessAction")

        # Get last day entries of ICU completeness
        filter = {
            "date_created": {
                "$gte": (date.today() - timedelta(days=1)).strftime("%Y-%m-%d"),
                "$lt": date.today().strftime("%Y-%m-%d"),
            }
        }
        cursor = db.icu_beds_completeness.find(filter)
        for doc in cursor:
            # Check the amount of completeness
            report = self.process_entry(doc)
            # Save alert or warning
            db.report.insert_one(report)

    def process_entry(self, entry):
        """Returns a report with alert of warning"""
        report = dict(
            processed_at=datetime.now(),
            country=entry["country"],
            region=entry["region"],
            document=entry,
        )

        if (
            entry["completeness_percentage"] > 41
            and entry["completeness_percentage"] < 60
        ):
            report["status"] = "warning"
            return report
        else:
            report["status"] = "alert"
            return report


class DeathsAction:
    """
    Deaths
        - Warning: Fixed or decreasing number of deaths from confirmed cases for the last 3 weeks
        - Alert: Increasing number of deaths from confirmed cases for the last 3 weeks

    Checks deaths of last 3 weeks in db. If they are incresing report an alert
    *** Note to self: What a great name for a class
    """

    def execute(self):
        # Get deaths from last 3 weeks (21 days)
        # If amount of of deaths is steady produce warning, else alert

        # TODO: define steady / increasing
        pass
