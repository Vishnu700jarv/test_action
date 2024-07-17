from datetime import datetime, timezone
import json
import uuid
from kafka import KafkaConsumer
from db import postgres
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
KAFKA_BROKER = os.environ.get('KAFKA_BROKER')
CONSUMER_GROUP = os.environ.get('CONSUMER_GROUP')
KAFKA_TOPIC = os.environ.get('KAFKA_TOPIC')
KAFKA_OFFSET = os.environ.get('KAFKA_OFFSET')

if not all([KAFKA_BROKER, CONSUMER_GROUP, KAFKA_TOPIC, KAFKA_OFFSET]):
    logger.error("One or more environment variables are missing.")
    raise ValueError("Environment variables KAFKA_BROKER, CONSUMER_GROUP, KAFKA_TOPIC, and KAFKA_OFFSET must be set.")


# Initialize a Kafka consumer
consumer = KafkaConsumer(
    KAFKA_TOPIC,
    bootstrap_servers=[KAFKA_BROKER],
    group_id=CONSUMER_GROUP,
    auto_offset_reset=KAFKA_OFFSET,
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)


def extract_id_from_filename(filename):
    base_name, extension = os.path.splitext(filename)
    try:
        image_name, image_id = base_name.rsplit("_", 1)
    except ValueError:
        image_name, image_id = base_name, None
    return image_name, image_id, extension

def save_stream_data_to_db(stream_data):
    if not stream_data:
        logger.warning("No inference data found.")
        return

    try:
        image_name_ai = stream_data.get("image_name")
        if not image_name_ai:
            logger.warning("Image name not found in inference data.")
            return
        
        image_name, image_id, extension = extract_id_from_filename(image_name_ai)
        new_id = str(uuid.uuid4())

        generated_timestamp = stream_data.get("timestamp")
        if generated_timestamp:
            # Ensure the timestamp is properly formatted
            try:
                timestamp_datetime = datetime.fromisoformat(generated_timestamp)
                formatted_timestamp = timestamp_datetime.isoformat()
            except ValueError:
                logger.error(f"Invalid timestamp format: {generated_timestamp}")
                return
        else:
            logger.warning("timestamp not found in inference data.")
            return
        
        # Find the index of the highest confidence value
        max_confidence_index = stream_data["confidence"].index(max(stream_data["confidence"]))

        # Get the prediction and confidence corresponding to the highest confidence value
        highest_confidence_prediction = stream_data["predictions"][max_confidence_index]
        highest_confidence_value = stream_data["confidence"][max_confidence_index]

        # Add the highest confidence prediction and value as new fields in the dictionary
        stream_data["highest_confidence_prediction"] = highest_confidence_prediction
        stream_data["highest_confidence_value"] = highest_confidence_value

        query = """
            INSERT INTO vision.yta_app_streamdata(
                id, inference_data, generated_timestamp, image_id
            ) VALUES (%s, %s, %s, %s)
        """
        
        params = (
            new_id,
            json.dumps(stream_data),
            formatted_timestamp,
            image_id,
        )

        score_query = """
                UPDATE vision.yta_app_auditscore
                SET 
                    ai_score = %s,
                    ai_comment = %s,
                    ai_score_date = CURRENT_TIMESTAMP
                WHERE 
                    image_upload_id = %s;
                """
        score_query_params = (
            highest_confidence_value,
            highest_confidence_prediction,
            image_id
        )
        # Ensure connection is established and query is executed
        postgres.connect()
        try:
            postgres.execute_query_with_params(query, params)
            logger.info(f"Successfully inserted data for image_id: {image_id}")

            postgres.execute_query_with_params(score_query, score_query_params)
            logger.info(f"Successfully updated audtit score data for image_id: {image_id}")
        finally:
            postgres.disconnect()
    except Exception as ex:
        logger.error(f"Error in save_stream_data_to_db: {ex}")

try:
    for message in consumer:
        stream_data = message.value
        logger.info(f"Received message: {stream_data}")
        save_stream_data_to_db(stream_data)
except Exception as ex:
    logger.error(f"Error while consuming messages: {ex}")
finally:
    consumer.close()
