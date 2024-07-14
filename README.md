# Evermore 

Evermore is an MLaaS web application built using a microservices architecture. Spring Boot and Flask used for backend development. React framework used for frontend development. AWS is used for cloud infrastructure. Users upload datasets to AWS S3 and AWS RDS used for PostgreSQL instance. Users develop and train models using frameworks like PyTorch, TensorFlow, Scikit-Learn within Docker containers, ensuring reproducibility. Machine Learning models run in separate Docker containers, providing flexibility for model development and deployment. The platform supports various ML algorithms. Users can buy and sell models and datasets, promoting a collaborative and incentivized environment. Payment managed through Stripe for seamless transactions.

You can see our projects presentation video here: https://studio.youtube.com/video/ybZdYfvYwg4/edit

## model-microservice

In this microservice, we implemented the logic for running models on a remote machine. 

### Functionalities: 
- User can upload their model by submitting the model's Docker Hub repository name. Each model runs in a separate Docker container and we return a port for the model to be run on. 
- User can list all their uploaded models. 
- User can delete their uploaded models. 
- User can upload, list and delete datasets. These are kept in AWS S3. 
- Model can be run with different parameters such as learning rate, optimizer etc. These are decided by the user. 
- After the run completes, we return evaluation metrics such as accuracy, F1 Score, MSE and precision. 