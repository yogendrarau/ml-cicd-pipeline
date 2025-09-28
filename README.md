# Machine Learning Model CI/CD Pipeline

This project implements a complete CI/CD pipeline for a machine learning model using GitHub Actions, Docker, and AWS ECS Fargate. The pipeline automatically tests, trains, evaluates, and deploys the model whenever new code is pushed to the `main` branch. A deployment only occurs if the new model achieves better performance than the model currently in production.

## Overview

The workflow is structured as follows:

1. **Linting and Testing**: Unit tests are executed to validate code quality.
2. **Model Training**: A machine learning model is trained on the Iris dataset using scikit-learn.
3. **Model Evaluation**: The trained model is evaluated on a test set, and metrics such as accuracy are recorded.
4. **Promotion Gate**: The new model’s accuracy is compared against the currently deployed production model. The model is only promoted if it exceeds the production baseline by a configurable margin defined in `configs/gates.yaml`.
5. **Deployment**: If the gate passes, a new Docker image containing the trained model and FastAPI inference service is built, pushed to Amazon ECR, and deployed to AWS ECS Fargate.

The deployed service exposes two endpoints:
- `/healthz` for health checks
- `/predict` for making predictions on new data

## Dataset and Model

The model is trained on the **Iris dataset**, which contains 150 samples of iris flowers. Each sample includes four features:

- Sepal length
- Sepal width
- Petal length
- Petal width

The goal is to classify each sample into one of three species:
- Iris Setosa
- Iris Versicolor
- Iris Virginica

A logistic regression classifier from scikit-learn is used as the baseline model. Training artifacts (the serialized model and metrics) are stored in the `artifacts/` directory during each pipeline run.

## Project Structure

├── src/\
│ ├── train.py # trains the model and saves artifacts\
│ ├── evaluate.py # evaluates the trained model and saves metrics\
│ └── inference.py # FastAPI app serving /predict and /healthz\
├── artifacts/ # contains model.pkl and metrics.json (generated at runtime)\
├── configs/\
│ └── gates.yaml # defines promotion rules (e.g., min_delta for accuracy)\
├── registry/\
│ └── production/\
│ └── manifest.json # tracks which model is currently in production\
├── scripts/\
│ └── compare_and_promote.py # compares new vs production model metrics\
├── ecs-taskdef.json # ECS task definition template with placeholder tag\
├── .github/\
│ └── workflows/\
│ └── ci_cd.yml # GitHub Actions workflow\
├── requirements.txt\
└── README.md\


## CI/CD Workflow

- **Trigger**: Runs on pull requests and pushes to the `main` branch.
- **Lint & Tests**: Executes pytest to validate code.
- **Train and Evaluate**: Runs `train.py` and `evaluate.py` to generate model artifacts and evaluation metrics.
- **Promotion Gate**: Executes `compare_and_promote.py`, which checks `metrics.json` against the production manifest. If accuracy improves by at least the threshold defined in `gates.yaml`, the new model is promoted.
- **Deploy**: Builds a Docker image tagged with the GitHub commit SHA, pushes it to Amazon ECR, registers a new ECS task definition revision, and updates the ECS Fargate service.

## Deployment Environment

- **Amazon ECR** is used as the container registry.
- **AWS ECS Fargate** runs the containers without the need to manage servers.
- The deployed FastAPI service listens on port 8080 and provides prediction and health endpoints.

## Example Usage

### Health check
curl http://<PUBLIC_IP>:8080/healthz

### Prediction
curl -X POST http://<PUBLIC_IP>:8080/predict
-H "Content-Type: application/json"
-d '{"sepal_length":5.1,"sepal_width":3.5,"petal_length":1.4,"petal_width":0.2}'
