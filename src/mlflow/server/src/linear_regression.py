from random import random, randint
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.datasets import load_breast_cancer

import mlflow
import mlflow.sklearn

mlflow.set_tracking_uri('http://127.0.0.1:31267')

if __name__ == "__main__":
    with mlflow.start_run(run_name="test_run") as run:
        cancer = load_breast_cancer()
        x_train, x_test, y_train, y_test = train_test_split(cancer.data, cancer.target)
        model = LinearRegression()
        model.fit(x_train, y_train)
        score = model.score(x_test, y_test)

        mlflow.log_metric("score", score)

        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="sklearn-linear-regression-model",
            registered_model_name="sk-learn-linear-regression-registered-model"
        )
