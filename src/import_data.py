import os
import requests
import logging

log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_fmt)

logger = logging.getLogger(__name__)

def main(raw_data_relative_path="./data/raw",
         filename="admission.csv",
         bucket_folder_url="https://assets-datascientest.s3.eu-west-1.amazonaws.com/MLOPS/bentoml"
         ):
    """ Download data from AWS s3 in ./data/raw
    """
    if not os.path.exists(raw_data_relative_path):
        os.makedirs(raw_data_relative_path)
    input_file = os.path.join(bucket_folder_url, filename)
    output_file = os.path.join(raw_data_relative_path, filename)
    if not os.path.exists(output_file):
        object_url = input_file
        print(f'downloading {input_file} as {os.path.basename(output_file)}')
        response = requests.get(object_url)
        if response.status_code == 200:
            # Process the response content as needed
            content = response.text
            text_file = open(output_file, "wb")
            text_file.write(content.encode('utf-8'))
            text_file.close()
        else:
            print(f'Error accessing the object {input_file}:', response.status_code)
    logger.info('making raw data set')


if __name__ == '__main__':

    main()