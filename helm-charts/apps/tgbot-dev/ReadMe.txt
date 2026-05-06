export KUBECONFIG=~/.kube/k3s.config


-- BUILD --
docker build -t tgbot-dev:0.1 .
docker login
docker images
docker tag tgbot-dev:0.1 YOUR_USERNAME/tgbot-dev:0.1
docker push YOUR_USERNAME/tgbot-dev:0.1

docker images
docker rmi IMAGE_ID
------------

kubectl create namespace tg

kubectl apply -f tg-properties.yaml
kubectl delete -f tg-properties.yaml


kubectl apply -f tgbot.yaml
kubectl delete -f tgbot.yaml

-----------
scp -r ~/projects/raspbbery/helm-charts/apps/tgbot-dev/* root@192.168.1.250:/opt/skyops/tgbot/