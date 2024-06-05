import json
import boto3
import time
from decimal import Decimal
from botocore.exceptions import ClientError

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table("TemperatureData")

# Variable global para el ID
last_id = 0


def get_next_id():
    global last_id
    last_id += 1
    return last_id


def lambda_handler(event, context):
    print("Received event: " + json.dumps(event))

    try:
        device_id = event["device_id"]
        temperature = Decimal(str(event["temperature"]))  # Convertir a Decimal
        humidity = Decimal(str(event["humidity"]))  # Convertir a Decimal
        timestamp = int(time.time())

        # Obtener el próximo ID único
        new_id = get_next_id()

        table.put_item(
            Item={
                "Id": new_id,  # Clave primaria única numérica
                "deviceId": device_id,
                "timestamp": timestamp,
                "temperature": temperature,
                "humidity": humidity,
            }
        )

        return {"statusCode": 200, "body": json.dumps("Data inserted successfully!")}
    except KeyError as e:
        return {
            "statusCode": 400,
            "body": json.dumps(f"Missing key in input: {str(e)}"),
        }
    except TypeError as e:
        return {"statusCode": 400, "body": json.dumps(f"Type error in input: {str(e)}")}
    except ClientError as e:
        return {
            "statusCode": 500,
            "body": json.dumps(f"Error: {e.response['Error']['Message']}"),
        }
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps(f"Error: {str(e)}")}
