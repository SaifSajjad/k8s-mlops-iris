FROM python:3.10-slim
RUN pip install --no-cache-dir mlflow==2.16.2 scikit-learn==1.5.2 pandas==2.2.2
ENV MLFLOW_TRACKING_URI=http://mlflow:5000
ENV MODEL_URI=models:/iris-classifier/Production
EXPOSE 5001
# Serves the Production model from the MLflow registry on :5001 (/invocations, /ping)
CMD ["sh","-c","mlflow models serve -m \"$MODEL_URI\" -h 0.0.0.0 -p 5001 --env-manager local"]
