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