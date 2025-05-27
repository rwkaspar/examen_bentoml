import shutil
import os


bentoml_store_path = "/bentoml/models"
project_model_path = os.path.abspath("models/admission_model")
if os.path.exists(project_model_path):
    shutil.rmtree(project_model_path)
shutil.copytree(bentoml_store_path, project_model_path)