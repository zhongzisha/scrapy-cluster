kubectl create -f zookeeper-service.yaml
kubectl create -f kafka-service.yaml
kubectl create -f kafka-service-2.yaml
kubectl create -f redis-service.yaml
kubectl create -f rest-service.yaml
kubectl create -f crawler-service.yaml
kubectl get svc -n scrapy-cluster -o wide


kubectl create -f zookeeper-deployment.yaml
kubectl create -f kafka-deployment.yaml
kubectl create -f kafka-deployment-2.yaml
kubectl create -f redis-deployment.yaml
kubectl create -f rest-deployment.yaml
kubectl create -f kafka-monitor-deployment.yaml
kubectl create -f redis-monitor-deployment.yaml

kubectl create -f crawler-deployment.yaml

kubectl get pods -n scrapy-cluster -o wide


