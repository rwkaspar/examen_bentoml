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
bentoml containerize admission_api:latest --docker-image-tag admission_api:latest
```
