# Rule engine

### Description:

The rule engine will receive metrics from all stamina components in predefined timeframes.
For example every end of day all Stamina components will broadcast their aggregated found metrics. Example metrics can be: 10 people found with high fever in Greece, 20 people tweeted about X symptom and so on.

The rule engine will have to store all those messages and in a predefined timeframe aggregate all messages and check thresholds. If the aggregated metrics are over the thresholds the Rule Engine will produce an alert or warning and send it to the message broker for other components to use. It is connected t the central message broker of STAMINA and listens for message from various components. A scheduler runs once per day aggregating and analysing all data gathered. Using a round robin algorythm the scheduler will check all use cases provided.

After the engine identifies an alert or warning it will save it in the database and forward a message to the Alert formulation system.
