import boto3
import logger
def upload_to_s3(bucket, filepath, obj_name):
    log = logger.get_logger()
    s3 = boto3.client('s3')
    log.info(f"File {filepath} to be uploaded to bucket: {bucket} as {obj_name}")
    try:
        s3.upload_file(filepath, bucket, obj_name)
        log.info("upload_to_s3:: File Uploaded to S3 successfully")

    except Exception as e:
        log.error("Something went wrong while uploading files to S3")
        raise Exception(f"error uploading file to s3 bucket: {e}")

