Question 1:

Without a volume, files written to /mlflow-data are stored in the container's writable filesystem. Stopping the container does not remove them, but removing the container deletes them. A new container created from the same image starts with a new MLflow database because runtime data is not stored in the image.

Question 2:

A named volume is useful because Docker manages its location and lifecycle independently of the project folder. A bind mount could also persist the data, but it would map /mlflow-data to a specific folder on the host machine and is usually more tied to the local development environment.

Question 3:


Docker Compose automatically creates a private network for the services and provides DNS resolution using service names. Therefore, the inference container can resolve mlflow directly to the MLflow container. In Lab 3, MLflow was running on the host machine, so we had to use host.docker.internal instead.


Question 4:

Using an environment variable keeps the frontend portable. Inside Compose, we set it to http://inference:8000, but if the frontend is run separately with docker run, we can give it another URL without modifying the Python code.

Question 5:

The inference service is only used by the frontend, so it does not need to be directly accessible from the host. The frontend reaches it through the private Compose network using http://inference:8000. MLflow and the frontend publish ports because we need to access them from the browser on the host machine.


Question 6:

depends_on only makes Docker start the MLflow container before inference. It does not guarantee that the MLflow server is already accepting requests. Since serve.py loads the model during startup, inference can fail and exit if MLflow is not ready yet. A more robust solution would use a health check, retry logic, or restart policy.


Question 7:


From our docker compose ps, MLflow published port 5000 and the frontend published port 8501. Inference only showed 8000/tcp, meaning it was available inside the Docker network but not published to Windows. This exactly matches the Compose configuration


Question 8:

No. Our serve.py loads the model only once when the inference service starts. Changing the model alias in MLflow does not replace the model already loaded in memory. We used the modern champion alias instead of the lab's older Staging wording. After moving champion to the new version, we restarted inference with:

docker compose restart inference

After the restart, the service loaded the model currently pointed to by champion.


Question 9:


The inference Docker image contains the application code and dependencies, but the actual deployed model is obtained from MLflow when the container starts. Because the application code did not change, there was no reason to rebuild the image. Restarting caused serve.py to resolve food11@champion again and load the current model version,


Question 10:

With:

docker compose down

the containers and network were deleted, but the named volume remained. After docker compose up, our registered model and champion alias were still present.  
With:

docker compose down -v

the named volume was also deleted. The MLflow database, registered models, aliases, runs, and model artifacts stored in that volume disappeared, and we had to create the model again. This directly demonstrated why the named volume is necessary for persistence.

Quuestion 11:

Docker Compose is mainly designed for running services on one machine. It does not provide full multi-machine orchestration, automatic scaling, high availability, or production load balancing. To run several inference replicas and survive machine failures, we would need an orchestrator such as Kubernetes, together with load balancing and durable external storage/database infrastructure for services such as MLflow.


