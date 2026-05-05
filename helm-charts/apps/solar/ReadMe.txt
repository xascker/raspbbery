export KUBECONFIG=~/.kube/k3s.config

mongosh --host 192.168.1.151 --port 30017 -u root -p admin --authenticationDatabase admin
db.createCollection("solar")
use space

db.solar.createIndex({ createdAt: 1 },{ expireAfterSeconds: 604800 } )  #7 days
show collections
db.solar.getIndexes()

db.solar.find().pretty()
db.solar.deleteOne({ _id: ObjectId("69f8ff117162f08c5160ec30") })


-- BUILD --
docker build -t sun-collector:0.1 .
docker login
docker images
docker tag sun-collector:0.1 YOUR_USERNAME/sun-collector:0.1
docker push YOUR_USERNAME/sun-collector:0.1

docker images
docker rmi IMAGE_ID
------------


kubectl create namespace astro
kubectl apply -f solar-properties.yaml
kubectl apply -f cronjob.yaml



-- check --
kubectl get cronjob -n astro
kubectl describe cronjob sun-collector -n astro

-- test --
kubectl create job --from=cronjob/sun-collector test-run -n astro
kubectl get jobs -n astro
kubectl delete job test-run -n astro

kubectl logs test-run-wjqzh -n astro