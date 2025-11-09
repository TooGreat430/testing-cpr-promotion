steps:
# 1. Substitute variables with image details. Replace AR_REGION and AR_REPO.
- name: 'gcr.io/cloud-builders/gcloud'
  id: Set_Variables
  entrypoint: 'bash'
  args:
  - '-c'
  - |
    # Source project info (where images are pulled from)
    export SOURCE_PROJECT_ID='bdi-onprem'
    export SOURCE_AR_HOST='asia-southeast2-docker.pkg.dev' # e.g., us-central1-docker.pkg.dev
    export SOURCE_REPOSITORY='custom-prediction-routine-sdk' # The repo name in the source project

    # Destination project info (where images are pushed to)
    export DEST_PROJECT_ID='me-data-internal-sandbox'
    export DEST_AR_HOST='asia-southeast2-docker.pkg.dev' # Must be the host for the destination AR
    export DEST_REPOSITORY='custom-prediction-routine-sdk' # The repo name in the destination project

    # The prefix to filter images
    export IMAGE_PREFIX='image_docker'

    # Pass the variables to the next step
    echo "SOURCE_PROJECT_ID=$SOURCE_PROJECT_ID" >> /workspace/vars.env
    echo "SOURCE_AR_HOST=$SOURCE_AR_HOST" >> /workspace/vars.env
    echo "SOURCE_REPOSITORY=$SOURCE_REPOSITORY" >> /workspace/vars.env
    echo "DEST_PROJECT_ID=$DEST_PROJECT_ID" >> /workspace/vars.env
    echo "DEST_AR_HOST=$DEST_AR_HOST" >> /workspace/vars.env
    echo "DEST_REPOSITORY=$DEST_REPOSITORY" >> /workspace/vars.env
    echo "IMAGE_PREFIX=$IMAGE_PREFIX" >> /workspace/vars.env
  env:
  - 'HOME=/root'

# 2. Pull and Push Images with a Filter
- name: 'gcr.io/cloud-builders/gcloud'
  id: Copy_Images
  entrypoint: 'bash'
  args:
  - '-c'
  - |
    # Load variables set in the previous step
    source /workspace/vars.env

    # Configure Docker for cross-project access (using Cloud Build's service account)
    # The Cloud Build service account will need Artifact Registry Reader in SOURCE_PROJECT_ID
    # and Artifact Registry Writer in DEST_PROJECT_ID.
    gcloud auth configure-docker ${SOURCE_AR_HOST} --quiet
    gcloud auth configure-docker ${DEST_AR_HOST} --quiet

    # Base URL for listing images in the source project
    SOURCE_REGISTRY_PATH=${SOURCE_AR_HOST}/${SOURCE_PROJECT_ID}/${SOURCE_REPOSITORY}
    DEST_REGISTRY_PATH=${DEST_AR_HOST}/${DEST_PROJECT_ID}/${DEST_REPOSITORY}

    echo "Listing images in source: ${SOURCE_REGISTRY_PATH}"

    # List images, filter by prefix, and extract the full image name
    gcloud artifacts docker images list ${SOURCE_REGISTRY_PATH} \
      --include-tags \
      --format='value(format("{0}:{1}", PACKAGE, TAG))' \
      --filter="PACKAGE~${IMAGE_PREFIX}" \
      --limit=9999 \
      > /workspace/images_to_copy.txt

    if [ ! -s /workspace/images_to_copy.txt ]; then
        echo "No images found with prefix ${IMAGE_PREFIX}. Exiting."
        exit 0
    fi

    echo "Found images to copy:"
    cat /workspace/images_to_copy.txt

    # Loop through each image and copy it
    while IFS= read -r FULL_IMAGE_NAME
    do
      if [ -z "$FULL_IMAGE_NAME" ]; then continue; fi

      # Full path of the source image
      SOURCE_IMAGE_TAG="${SOURCE_REGISTRY_PATH}/${FULL_IMAGE_NAME}"

      # Use the same image/tag name for the destination, but with the new project path
      DEST_IMAGE_TAG="${DEST_REGISTRY_PATH}/${FULL_IMAGE_NAME}"

      echo "Pulling ${SOURCE_IMAGE_TAG}"
      docker pull "${SOURCE_IMAGE_TAG}"

      echo "Tagging ${FULL_IMAGE_NAME} for destination project"
      docker tag "${SOURCE_IMAGE_TAG}" "${DEST_IMAGE_TAG}"

      echo "Pushing ${DEST_IMAGE_TAG}"
      docker push "${DEST_IMAGE_TAG}"

      echo "Completed push of ${DEST_IMAGE_TAG}"

    done < /workspace/images_to_copy.txt
  env:
  - 'HOME=/root'