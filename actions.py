from mongo import db
import pymongo
from pymongo import MongoClient
from datetime import date, datetime, timedelta

from utils import *
import logging
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
        status = "alert"
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
        status = "alert"
        return status
    else:
        status = "no actions needed"
        return status


def check_HR_data(hr):
    # hr stands for heart_rate
    if hr > 100 and hr < 105:
        status = "warning"
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

def check_param_BO_data(bo, trial_params):
    # bo stands for blood_oxygen
    bo_params = trial_params["blood_oxygen"]
    if  bo > bo_params["alert_low"] and bo <= bo_params["warning_low"]:
        status = "warning"
        return status
    elif bo <= bo_params["alert_low"]:
        status = "alert"
        return status
    else:
        status = "no actions needed"
        return status

def check_param_HR_data(hr, trial_params):
    # hr stands for heart_rate
    hr_params = trial_params["heart_rate"]
    if ( hr > hr_params["alert_low"] and hr <= hr_params["warning_low"]) | ( hr > hr_params["regular_low"] and hr <= hr_params["warning_high"]):
        status = "warning"
        return status
    elif (hr >= hr_params["alert_high"] or hr <= hr_params["alert_low"]):
        status = "alert"
        return status
    else:
        status = "no actions needed"
        return status

def check_param_ST_data(st, trial_params):
    # st stands for skin_temperature
    st_params = trial_params["temperature"]
    if (st > st_params["alert_low"] and st <= st_params["warning_low"]) | (st > st_params["regular_low"] and st <= st_params["warning_high"]):
        status = "warning"
        return status
    elif (st <= st_params["alert_low"] or st > st_params["warning_high"]):
        status = "alert"
        return status
    else:
        status = "no actions needed"
        return status

def find_total_status(measurement, status, mac_address, time, database):
    ''' Compares the status of the current measurement with the status of the last measurement'''

    last_measurement = find_last_doc_from_db(mac_address, database, measurement, time, True)
    total_status = "no actions needed"
    logging.warning("Until here")
    if last_measurement != None:
            last_status = last_measurement["status"]
            last_time = last_measurement["time"]
        
            logging.warning('Last measurement is: %s', last_measurement)

            last_time = datetime.fromtimestamp(last_time)
            time = datetime.fromtimestamp(time)
            if (time - last_time < timedelta(seconds=3600)):
                if status == "warning" and last_status == "warning":
                    total_status = "warning"
                elif status == "alert" and last_status == "alert":
                    total_status = "alert"
                elif (status == "warning" and last_status == "alert") | (status == "alert" and last_status == "warning"):
                    total_status = "alert"

    return total_status

def calculate_param_rules_on_smartko_data(measurement, value, trial, mac_address, time, database):
    params = load_params()
    logging.info("Calculating param rules")
    if trial =="AU":
        trial_params = params["AU"]
    
    # TODO: Need to create general params
    
    if measurement == "blood_oxygen":
        status = check_param_BO_data(value, trial_params)
        total_status = find_total_status("blood_oxygen", status, mac_address, time, database)

    elif measurement == "heart_rate":
        status = check_param_HR_data(value, trial_params)
        total_status = find_total_status("heart_rate", status, mac_address, time, database)

    elif measurement == "skin_temperature":
        status = check_param_ST_data(value, trial_params)
        total_status = find_total_status("skin_temperature", status, mac_address, time, database)
    else:
        status = "no actions needed"
        total_status = "no actions needed"

    return status, total_status

def find_last_doc_from_db(mac_address, database, measurement, time, less_value):
    """
    Finds the last time's (previous or after) measurement status before 120 sec of specific mac address
    """

    health_collection = database.health
    list_of_docs = []
    time_to_use = time-120

    if less_value:
        query = {"mac_address": mac_address, "measurement": measurement, "time": { "$lt": time_to_use }}
    else:
        query = {"mac_address": mac_address, "measurement": measurement, "time": { "$gt": time_to_use }}

    for doc in health_collection.find(query).sort(
        "time", pymongo.DESCENDING
    ):
        doc.pop("_id")
        list_of_docs.append(doc)
    if len(list_of_docs) > 0:
        last_time_doc = list_of_docs[0]
        return last_time_doc
    else:
        return None

# Not used
def get_measurement_and_convert_time_to_timestamp(measurement):
    time = measurement["time"]
    time = datetime.fromtimestamp(time)
    return time

# Not used
def check_time_difference(time_1, time_2):
    if (abs(time_1 - time_2) > timedelta(seconds=120)) & (abs(time_1 - time_2) < timedelta(seconds=3600)):
        return True
    else:
        return False

# TODO: Need to connect and check combined measurements
def calculate_combined_measurements(mac_address, database, hr, oxy, time):
    status = "no actions needed"
    first_doc = None
    second_doc = None
    if hr==True:
        last_time_hr = find_last_doc_from_db(mac_address, database, "heart_rate", time, False)
        first_doc = last_time_hr
        if last_time_hr != None:
            if oxy==True:
                last_time_oxy = find_last_doc_from_db(mac_address, database, "blood_oxygen", time, False)
                second_doc = last_time_oxy

                if last_time_oxy != None:
                    if ((last_time_hr["value"]>100) & (last_time_oxy["value"]<93)) | ((last_time_hr["value"]<60) & (last_time_oxy["value"]<93)):
                         status = "alert"
            else:
                last_time_temp = find_last_doc_from_db(mac_address, database, "skin_temperature", time, False)
                second_doc = last_time_temp
                if last_time_temp != None:
                    if ((last_time_hr["value"]>90) & (last_time_temp["value"]>37.8)) | ((last_time_hr["value"]>90) & (last_time_temp["value"]<35.9)):
                        status = "alert"
    else:
        last_time_oxy = find_last_doc_from_db(mac_address, database, "blood_oxygen", time, False)
        first_doc = last_time_oxy
        if last_time_oxy != None:
            last_time_temp = find_last_doc_from_db(mac_address, database, "skin_temperature", time, False)
            second_doc = last_time_temp
            if last_time_temp != None:
                if ((last_time_oxy["value"]<94) & (last_time_temp["value"]>37.8)) | ((last_time_oxy["value"]<94) & (last_time_temp["value"]<36)):
                    status = "alert"
    return status, first_doc, second_doc