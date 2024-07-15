from datetime import datetime, timezone
import json
import uuid
from kafka import KafkaConsumer
from db import postgres
import os



# KAFKA_BROKER = '20.244.150.206:9094'
# CONSUMER_GROUP = 'sqvision_cg_apd_dev'
# KAFKA_TOPIC = 'global_apd_kar'
# KAFKA_OFFSET = 'latest'

KAFKA_BROKER = os.environ.get('KAFKA_BROKER')
CONSUMER_GROUP = os.environ.get('CONSUMER_GROUP')
KAFKA_TOPIC = os.environ.get('KAFKA_TOPIC')
KAFKA_OFFSET = os.environ.get('KAFKA_OFFSET')

sleep_time = 10


# Initialize a Kafka consumer
consumer = KafkaConsumer(
            KAFKA_TOPIC,  # Kafka topic name
            bootstrap_servers=[KAFKA_BROKER],
            group_id=CONSUMER_GROUP,
            auto_offset_reset=KAFKA_OFFSET,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )


def save_stream_data_to_db(stream_data):
    postgres.connect()
    
    # Extract the inference data from the stream data
    print("inside db stream update function")
    inference_data = stream_data["Inference_Data"]
    
    if len(inference_data) != 0:
        # Extract the image name from the inference data
        try:
            image_name_ai = inference_data["ImageName"]

            # Check if the image name is not "image1.png"
            try:
                # Split the image name and ID
                image_name_ai, _ = image_name_ai.rsplit(".", 1)
                image_name, image_id = image_name_ai.rsplit("_", 1)

                
                new_id = str(uuid.uuid4())

                # Use the new UUID for insertion
                query = """INSERT INTO vision.native_app_streamdata(id,
                                "Inference_Data", "Category", "Site", "EngineIdentity",
                                "Camera_State", "GeneratedTimestamp", "image_id")
                           VALUES (%s,%s, %s, %s, %s, %s, %s, %s)
                        """
                # Execute the query with the new_image_id
                postgres.execute_query_with_params(query, (
                    new_id,
                    json.dumps(inference_data),
                    inference_data["Category"],
                    inference_data["Site"],
                    inference_data["EngineIdentity"],
                    inference_data["Camera_State"],
                    inference_data["GeneratedTimestamp"],
                    image_id,
                ))
            except Exception as ex:
                print("Error in pass state:", ex)
        except Exception as ex:
            print("Error in image name:", ex)
    else:
        print("No inference data found.")

    postgres.disconnect()


try:
    # Start consuming Kafka messages
    for message in consumer:
        # Deserialize the message value as JSON
        stream_data = message.value
        print("*"*100)
        print(stream_data)
        print("*"*100)
        # Call the method to save the stream data to the database
        save_stream_data_to_db(stream_data)
except Exception as ex:
    print(ex)
finally:
    # Close the Kafka consumer gracefully on a KeyboardInterrupt (Ctrl+C)
    consumer.close()