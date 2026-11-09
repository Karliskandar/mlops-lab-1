Question 1:

A unit test should not depend on the real MLflow model because it introduces external dependencies unrelated to the code being tested. The test could fail if the MLflow server is offline or unreachable, if the champion model or its artifacts are missing, or if there is a network/configuration problem even though the application code itself is correct. It would also make the tests slower and less reproducible.


Question 2:


The test proves that the API can receive and decode an uploaded image, preprocess it, call the model, interpret the returned values, and return a valid JSON response containing a category and confidence. It does not prove that the real ML model is accurate or that it can correctly classify Bread images, because the real model is replaced by a fake model with a fixed output.



Question 3:

The check that detected the problem was the cross-split duplicate check, which compares the MD5 hash of every image. A duplicate between training and evaluation is more dangerous because the program still runs normally, but the model may already have seen the same image during training. This creates data leakage and can make the evaluation accuracy look artificially high. A corrupted image is easier to notice because it usually causes an obvious error or crash.



Question 4:

The validation can run locally after preprocessing and before the dataset is pushed to DVC, so invalid data is never published. It can also run in a training or data pipeline on a machine that has access to the DVC remote, after the data has been pulled and before training starts.


Question 5:


Because smoke declares needs: test, it only runs if the test job succeeds. If Ruff or pytest fails, the smoke job is skipped. Without needs, the two jobs would be independent and could run in parallel, so the Docker smoke test could still run even if the unit tests failed.


Question 6:

The first CI run took 2 min 21 s, while the second took 2 min 31 s. The second run successfully restored the uv cache, whereas the first run had no cache available. However, uv sync was already fast and the restored cache was very small, so there was no significant reduction in the total time. The second Docker build also took longer, which made the overall second run slightly slower. This shows that caching can reduce repeated dependency work, but the total CI duration can still vary because every GitHub Actions run uses a fresh runner.



Question 7:

Tagging an image with the Git commit SHA creates a direct link between the Docker image and the exact version of the source code that produced it. The latest tag can change whenever a new image is pushed. For example, if machine A pulls latest before a new deployment and machine B pulls latest afterward, both machines may say they are running latest while actually running different versions of the application. A commit SHA avoids this ambiguity and makes deployments reproducible.

Question 8:


The workflow explicitly gives GITHUB_TOKEN only the permissions it needs: read access to the repository contents and write access to packages so it can publish the Docker image. This follows the principle of least privilege. If a compromised workflow step received broad write permissions, it could potentially modify repository contents, manipulate releases or other resources, or publish malicious packages using the repository's credentials.





Question 9:

The pull request showed that the required test job failed, so the dependent smoke job was skipped and GitHub blocked the merge into main. This is useful because errors are detected automatically before broken code reaches the protected main branch, so teammates do not have to rely only on everyone remembering to run the tests locally.



Question 10:

The current champion was version 1 with a test accuracy of 0.553832. With a test-set size of 1055 images, the standard error was 0.015304, so 2 * se was approximately 0.030608, or about 3.06 accuracy percentage points. Therefore, a candidate needed at least 0.584441 accuracy to become champion.

Candidate version 2 had a test accuracy of 0.109005, so it failed the gate and was assigned the challenger alias.

Candidate version 3 had a test accuracy of 0.746919, which was well above the required threshold, so it passed the gate and was promoted to champion.



Question 11:

One solution is to use a self-hosted GitHub Actions runner on the same machine or local network as the MLflow server, so the workflow can reach it directly. Another solution is to move MLflow to a hosted service accessible from GitHub Actions, such as the MLflow server provided by DagsHub, and store the required credentials securely in GitHub Secrets.


Question 12:

```text
[HUMAN]
Developer changes code
        |
        v
     git push
        |
        v
[AUTOMATIC - GitHub Actions]
+-------------------------+
| test                    |
| - checkout code         |
| - uv sync               |
| - Ruff                  |
| - pytest                |
+-------------------------+
        |
        v
+-------------------------+
| smoke                   |
| - build Docker image    |
| - start with SKIP_MODEL |
| - check /health         |
+-------------------------+
        |
        v
If branch = main
        |
        v
+------------------------------+
| push image to GHCR           |
| tag = Git commit SHA         |
+------------------------------+
        |
        |  CODE VERSION DECIDED HERE
        |  by the Git commit SHA
        v
[HUMAN / DEPLOYMENT STEP]
Pull and run the selected SHA-tagged Docker image
        |
        v
Container starts FastAPI
        |
        v
Loads:
models:/food11@champion
        |
        v
[MODEL VERSION]
MLflow champion alias
        ^
        |
[HUMAN TRAINING]
Train candidate model
        |
        v
Register candidate in MLflow
        |
        v
[AUTOMATIC GATE WHEN promote.py IS RUN]
Compare candidate test_accuracy
against champion + 2 * standard error
        |
        +---- passes ----> move champion alias
        |
        +---- fails -----> assign challenger alias

The code version is determined by the Git commit SHA used as the Docker image tag. The model version is determined independently by the MLflow `champion` alias. Training and starting the promotion process are still manual in the current setup, while testing, container validation, image building and publishing, and the promotion decision itself are automated.
