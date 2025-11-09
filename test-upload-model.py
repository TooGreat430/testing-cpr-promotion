from google.cloud import aiplatform, storage
import json
import sys

aiplatform.init(
    project='me-data-internal-sandbox',
    location='asia-southeast2' 
)

models = aiplatform.Model.list(
    project="me-data-internal-sandbox", 
    order_by="update_time desc",
    filter=f'display_name="customer-churn"'
)

parent_model = None
model_display_name="customer-churn"

for model in models:
    if model.display_name.lower() == model_display_name.lower():
        parent_model = model
        break

uploaded_model = aiplatform.Model.upload(
    project="me-data-internal-sandbox",
    display_name=model_display_name,
    artifact_uri=f"gs://yoshi-sandbox",
    serving_container_image_uri="asia-southeast2-docker.pkg.dev/me-data-internal-sandbox/custom-prediction-routine-sdk/test:latest",
    parent_model=parent_model.resource_name if parent_model else None,
    is_default_version=True,
    labels={
        "version": "13"
    },
    sync=True

) 


