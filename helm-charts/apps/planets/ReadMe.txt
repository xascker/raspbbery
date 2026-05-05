export KUBECONFIG=~/.kube/k3s.config

mongosh --host 192.168.1.151 --port 30017 -u root -p admin --authenticationDatabase admin
use space

db.createCollection("planets")
db.planets.createIndex({ createdAt: 1 },{ expireAfterSeconds: 604800 } )  #7 days
show collections
db.planets.getIndexes()

db.planets.find().pretty()
db.planets.deleteOne({ _id: ObjectId("69f8ff117162f08c5160ec30") })


-- BUILD --
docker build -t planets-collector:0.1 .
docker login
docker images
docker tag planets-collector:0.1 YOUR_USERNAME/planets-collector:0.1
docker push YOUR_USERNAME/planets-collector:0.1

docker images
docker rmi IMAGE_ID
------------


kubectl create namespace astro
kubectl apply -f planets-properties.yaml
kubectl apply -f cronjob.yaml
kubectl delete -f cronjob.yaml


-- check --
kubectl get cronjob -n astro
kubectl describe cronjob planets-collector -n astro

-- test --
kubectl create job --from=cronjob/planets-collector test-run -n astro
kubectl get jobs -n astro
kubectl delete job test-run -n astro

kubectl logs test-run-wjqzh -n astro