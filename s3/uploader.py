import boto3
from botocore.exceptions import NoCredentialsError

def upload_file_to_s3(file_name, bucket, object_name=None):
    # If object_name is not specified, use the local file name
    if object_name is None:
        object_name = file_name

    # S3 client initialization
    s3_client = boto3.client('s3')

    try:
        s3_client.upload_file(file_name, bucket, object_name)
        print(f"✅ Plik '{file_name}' został wysłany do S3 jako '{object_name}' w buckecie '{bucket}'")
    except FileNotFoundError:
        print("❌ Plik nie został znaleziony.")
    except NoCredentialsError:
        print("❌ Brak poświadczeń AWS.")
    except Exception as e:
        print(f"❌ Wystąpił błąd: {e}")
