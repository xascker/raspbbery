export KUBECONFIG=~/.kube/k3s.config

mongosh --host 192.168.1.151 --port 30017 -u root -p admin --authenticationDatabase admin
use space

db.createCollection("moon")
db.moon.createIndex({ createdAt: 1 },{ expireAfterSeconds: 604800 } )  #7 days
show collections
db.moon.getIndexes()

db.moon.find().pretty()
db.moon.deleteOne({ _id: ObjectId("69f8ff117162f08c5160ec30") })


-- BUILD --
docker build -t moon-collector:0.1 .
docker login
docker images
docker tag moon-collector:0.1 YOUR_USERNAME/moon-collector:0.1
docker push YOUR_USERNAME/moon-collector:0.1

docker images
docker rmi IMAGE_ID
------------


kubectl create namespace astro
kubectl apply -f moon-properties.yaml
kubectl apply -f cronjob.yaml
kubectl delete -f cronjob.yaml


-- check --
kubectl get cronjob -n astro
kubectl describe cronjob moon-collector -n astro

-- test --
kubectl create job --from=cronjob/moon-collector test-run -n astro
kubectl get jobs -n astro
kubectl delete job test-run -n astro

kubectl logs test-run-wjqzh -n astro