Question 1:



The model was registered as version 1. A logged model artifact is the model produced and stored as part of a particular MLflow run. A registered model gives that model a persistent name and version in the Model Registry, allowing different trained versions to be managed independently of their original runs.



Question 2:

MLflow replaced the old fixed stages such as Staging and Production with model aliases, such as champion or challenger. A model is versioned separately from the training run so multiple trained models can be managed under one stable model name. An alias is more flexible because it is a movable pointer: champion can be reassigned from version 1 to version 2 without changing the serving code.


Question 3:

The model is loaded through the MLflow URI models:/food11@champion instead of directly from a .pth file so the serving code is separated from the physical model file and from the training run that created it. To serve a newer model, we can register the new model version and move the champion alias to that version. The serving code does not need to change.

Question 4:

Docker cache: we copy pyproject.toml and uv.lock and install dependencies before copying src/ so Docker can cache the expensive dependency-installation layer. If only serve.py changes, Docker can reuse the dependency layer and rebuild only the later source-code layer.

Question 5:


he naive single-stage image was 11.1 GB, while the multi-stage image was 9.57 GB, saving about 1.53 GB. docker history showed that the largest layer in both images was the Python virtual environment, at around 6.2 GB. The multi-stage build is smaller because build tools and the larger builder environment are not copied into the final runtime image.






Question 6:

.dockerignore: without it, Docker would send unnecessary folders such as datasets, .venv, Git history, and MLflow outputs into the build context. That makes builds slower and can unnecessarily increase image size. These folders normally would not “break” the build just by being sent, but large/local-environment folders can cause conflicts or make COPY . . style builds huge and unpredictable.


Question 7:

A container cannot use 127.0.0.1:5000 to reach the MLflow server running on the host because 127.0.0.1 inside the container refers to the container itself. On Windows, host.docker.internal is a special hostname provided by Docker that resolves to the host machine, allowing the container to communicate with the MLflow server running there.


Question 8:

Yes. A new container created from the same Docker image can load and serve the model without rebuilding the image. The application code and Python environment are baked into the Docker image, while the registered food11@champion model is retrieved from MLflow at runtime. Therefore, the container can be recreated while using the same image, as long as the MLflow server and model artifact remain accessible.


Question 9:

e Docker image still needs to be published to a container registry such as Docker Hub or GitHub Container Registry. Git versions the Dockerfile, but it does not store the built image itself. For reliable deployment, the image should also use an immutable version tag or digest instead of relying only on latest, so a CI runner or Kubernetes cluster can pull the exact same image.

