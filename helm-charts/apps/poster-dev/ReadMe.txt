export KUBECONFIG=~/.kube/k3s.config

mongosh --host 192.168.1.151 --port 30017 -u root -p admin --authenticationDatabase admin
use space
db.createCollection("events")

db.events.createIndex({ createdAt: 1 },{ expireAfterSeconds: 259200 } )  #3 days
show collections
db.events.getIndexes()

db.events.find().pretty()
db.events.deleteOne({ _id: ObjectId("69f8ff117162f08c5160ec30") })
db.events.deleteMany({})
db.events.deleteMany({type: "planet_window"})
db.events.deleteMany({type: { $regex: "^moon" }})

-- BUILD --
docker build -t poster-dev:0.1 .
docker login
docker images
docker tag poster-dev:0.1 YOUR_USERNAME/poster-dev:0.1
docker push YOUR_USERNAME/poster-dev:0.1

docker images
docker rmi IMAGE_ID
------------

kubectl apply -f poster-properties.yaml
kubectl delete -f poster-properties.yaml


kubectl apply -f poster.yaml
kubectl delete -f poster.yaml


kdelp -l app=poster --force
-----------
#scp -r ~/projects/raspbbery/helm-charts/apps/poster-dev/* root@192.168.1.250:/opt/skyops/poster/
scp -r ~/projects/raspbbery/helm-charts/apps/poster-dev/* root@192.168.1.151:/opt/skyops/poster/