# Examen BentoML - Admission Prediction Service

This project implements a machine learning model service to predict admission chances based on applicant data. The service is built with BentoML and a Scikit-learn model.

---

## Project Structure

- `src/`: Source code including data import, preparation, model training, and BentoML service.
- `tests/`: Unit and integration tests for the service.
- `run_pipeline.py`: Script to run the entire pipeline (data import, preparation, training) easily.

---

## Setup Instructions

1. **Create and activate your virtual environment:**

```bash
python -m venv .venv
source .venv/bin/activate
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Run the full pipeline to prepare data and train the model:**

```bash
python run_pipeline.py
```

>This executes the following steps sequentially:
>* src/import_data.py: Imports the raw data.
>* src/prepare_data.py: Prepares and processes the data for training.
>* src/train_model.py: Trains the machine learning model and saves it.

4. **Build the BentoML service:**

```bash
bentoml build
```

5. **Serve the model API locally:**

```bash
bentoml serve admission_api:latest
```

>The service listens on http://localhost:3000.

---

## API Usage

### Prediction Endpoint
* URL: POST /predict
* Content-Type: application/json
* Payload example:
```json
{
  "input_data": {
    "GRE_Score": 320,
    "TOEFL_Score": 110,
    "University_Rating": 4,
    "SOP": 4.0,
    "LOR": 4.5,
    "CGPA": 9.0,
    "Research": 1
  }
}
```
* Response example:
```json
{
  "admission_chance": 0.85
}
```

## Testing

Run all tests with:
```bash
pytest tests/ -v
```

## Notes

* JWT authentication is currently not implemented.
* The service uses BentoML’s latest API style.
* If you want to containerize the service, use:
```bash
bentoml containerize admission_prediction:latest --docker-image-tag kaspar_admission_prediction
```

---

## Save the docker image
```bash
docker save -o bento_image.tar kaspar_admission_prediction
```

## Running the Project with Docker

When running the Docker container, you need to make sure that the BentoML model store is accessible inside the container. By default, BentoML looks for saved models in `/home/bentoml/models` inside the container.

If you have already trained a model on your host machine and it is stored in `~/bentoml/models`, you must mount this directory into the container so BentoML can find it.

### Starting the container with model volume mounted

```bash
docker run --rm -p 3000:3000 \
  -v ~/bentoml/models:/home/bentoml/models \
  kaspar_bentoml_exam_image:latest
```

This command maps your local model directory (~/bentoml/models) to the expected directory inside the container (/home/bentoml/models).

### Notes
* Without mounting the model directory, the container will not find any saved models and will fail to start the BentoML service.
* Alternatively, you can train and save the model inside the container to ensure the model exists in the container’s BentoML store.
* Make sure your model is saved under the name expected by the BentoML service (admission_model in this project).