from mongo import db
import pymongo
from pymongo import MongoClient
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


class WSMAAction:
    """
    WSMA

    EWS will not calculate rules for the case of WSMA.
    WSMA will send a message to Kafka with the warnings about every 6 hours
    (a warnings report will be send always, but there not always is an alert or warning.
    EWS has to check it).
    For each key in words_stats (eg. in schema “flu”, “symptoms”, “Covid”)
    check warning0 if at least one of them is True, then we have a warning.
    """

    def execute(self):
        print("Running WSMAAction")

        cursor = db.wsma.find()
        for doc in cursor:
            # Check the amount of positives
            report = self.process_entry(doc)
            # Save alert or warning
            db.report.insert_one(report)

    def process_entry(self, entry):
        for word in entry["words_stats"]:
            if (
                word["all"]["warning0"] == "True"
                or word["geo_country"]["warning0"] == "True"
            ):
                report = dict(
                    processed_at=datetime.now(),
                    status="warning",
                    # country=entry["country"],
                    # region=entry["region"],
                    document=entry,
                )
                return report


def check_BO_data(bo):
    # bo stands for blood_oxygen
    if bo <= 90 and bo >= 85:
        status = "warning"
        return status
    elif bo < 85:
        status = "Alert"
        return status
    else:
        status = "no actions needed"
        return status


def check_ST_data(st):
    # st stands for skin_temperature
    if st > 37 and st < 37.5:
        status = "warning"
        return status
    elif st < 28 or st >= 37.5:
        status = "Alert"
        return status
    else:
        status = "no actions needed"
        return status


def check_HR_data(hr):
    # hr stands for heart_rate
    if hr > 100 and hr < 105:
        status = "Warning"
        return status
    elif hr >= 105 or hr < 60:
        status = "alert"
        return status
    else:
        status = "no actions needed"
        return status


def calculate_rules_on_smartko_data(measurement, value):
    if measurement == "blood_oxygen":
        status = check_BO_data(value)
    elif measurement == "heart_rate":
        status = check_HR_data(value)
    elif measurement == "skin_temperature":
        status = check_ST_data(value)
    else:
        status = "no actions needed"
    return status


def find_geolocation_from_db(mac_address, database):
    """
    Finds the last time's geolocation of specific mac address
    and then return latitude and longitude
    """

    geolocation_collection = database.geo
    list_of_docs = []
    for doc in geolocation_collection.find({"mac_address": mac_address}).sort(
        "time", pymongo.DESCENDING
    ):
        doc.pop("_id")
        list_of_docs.append(doc)
    if len(list_of_docs) > 0:
        last_time_geo = list_of_docs[0]
        return last_time_geo["latitude"], last_time_geo["longitude"]
    else:
        return None, None
