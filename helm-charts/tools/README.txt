helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add influxdata https://helm.influxdata.com/
helm repo add grafana https://grafana.github.io/helm-charts
helm repo add bitnami https://charts.bitnami.com/bitnami

helm repo update

----------------------
root@master:~# crictl images
crictl rmi bdc4e039b30b9
----------------------

kubectl apply -f mongodb4-standalone.yaml
kubectl delete -f mongodb4-standalone.yaml
----------------------

kubectl apply -f https://openebs.github.io/charts/openebs-operator-lite.yaml
kubectl apply -f sc-openebs.yaml

helm upgrade --install grafana grafana/grafana -f grafana.yaml --namespace monit --create-namespace --version 10.1.4
helm upgrade --install prometheus prometheus-community/prometheus -f prometheus.yaml -n prom --create-namespace --version 14.12.0

helm upgrade --install  influxdb influxdata/influxdb -f influxdb.yaml --namespace monit --create-namespace --version 4.12.5
kubectl patch svc influxdb -n monit -p '{"spec":{"ports":[{"name":"http","port":8086,"targetPort":8086,"nodePort":30086},{"name":"admin","port":8088,"targetPort":8088,"nodePort":30088}]}}'

helm upgrade --install mongodb bitnami/mongodb -f mongodb.yaml --namespace mongo --create-namespace

==============================================================================

kubectl exec -it mongodb-5ddc4dbcdf-sggwn -n mongo -- mongo
use admin
db.createUser({
user: "root",
pwd: "admin",
roles: [ { role: "root", db: "admin" } ]
})

mongosh --host 192.168.1.151 --port 30017 -u root -p admin --authenticationDatabase admin

show dbs;
db.version();
db.hello();

use testdb
db.testcollection.insertOne({ name: "test", value: 123 })
db.testcollection.find()


===============================================================================
AdGuardHome
kubectl apply -f adguardhome.yaml
