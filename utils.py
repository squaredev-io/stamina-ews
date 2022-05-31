import yaml
from typing import Dict, Any
from confuent_producer import kafka_producer

def load_params(
    path: str = "params.yaml",
) -> Dict[str, Dict[str, Any]]:
    """Loads params base on yaml's path"""

    with open(path, "r") as stream:
        params = yaml.safe_load(stream)
        return params

def send_combined_alerts_to_kafka(combined_docs):
    if combined_docs!= None:
        kafka_producer(combined_docs)

# Combine both measurement into one dict and set the same combined status 
# for both of them
def combine_docs_to_kafka(first_doc, second_doc, combined_status):
    if (first_doc!=None) & (second_doc!=None):
        first_doc["status"] = combined_status
        second_doc["status"] = combined_status
        combined_docs = [first_doc, second_doc]
        send_combined_alerts_to_kafka(combined_docs)


