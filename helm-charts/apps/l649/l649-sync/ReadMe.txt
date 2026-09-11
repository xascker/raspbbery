export KUBECONFIG=~/.kube/k3s.config

mongosh --host 192.168.1.151 --port 30017 -u root -p admin --authenticationDatabase admin
show dbs
use lotto
db.createCollection("l649")

db.l649.createIndex({ createdAt: 1 },{ expireAfterSeconds: 47520000 } )  #1,5 year
show collections
db.l649.getIndexes()

db.l649.find().pretty()
db.l649.find().sort({ createdAt: -1 }).limit(1).pretty()
db.l649.deleteOne({ _id: ObjectId("69f8ff117162f08c5160ec30") })
db.l649.deleteMany({})

-- BUILD --
docker build -t l649-collector:0.1 .
docker login
docker images
docker tag l649-collector:0.1 YOUR_USERNAME/l649-collector:0.1
docker push YOUR_USERNAME/l649-collector:0.1

docker images
docker rmi IMAGE_ID
------------


kubectl create namespace lotto
kubectl apply -f l649-properties.yaml
kubectl apply -f cronjob.yaml
kubectl delete -f cronjob.yaml


-- check --
kubectl get cronjob -n lotto
kubectl describe cronjob l649-collector -n lotto

-- test --
kubectl create job --from=cronjob/l649-collector test-run -n lotto
kubectl get jobs -n lotto
kubectl delete job test-run -n lotto

kubectl logs test-run-wjqzh -n lotto