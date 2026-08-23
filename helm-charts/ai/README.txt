
kubectl apply -f ollama.yaml
kubectl delete -f ollama.yaml

kubectl apply -f ollama-nonGPU.yaml
kubectl delete -f ollama-nonGPU.yaml

=====================================================
kubectl exec -it -n ai deploy/ollama -- bash

ollama pull qwen3:8b
ollama run qwen3:8b

ollama pull qwen3:14b
ollama run qwen3:14b


crictl rmi ollama/ollama:latest
crictl images | grep ollama

kubectl delete namespace ai

====================================================

kubectl apply -f webui.yaml
kubectl delete -f webui.yaml

crictl images | grep webui
crictl rmi ghcr.io/open-webui/open-webui:main


====================================================

# wsl - windows
for /f "tokens=1" %i in ('wsl -d Ubuntu-22.04 -- hostname -I') do for %p in (22 10250 11434 30081) do netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=%p connectaddress=%i connectport=%p

netsh interface portproxy delete v4tov4 listenaddress=0.0.0.0 listenport=11434
netsh interface portproxy add v4tov4 listenaddress=0.0.0.0 listenport=11434 connectaddress=172.21.141.15 connectport=31434

netsh interface portproxy show all
====================================================

curl -v --connect-timeout 5 http://192.168.1.227:11434/api/tags

kubectl exec -it deployment/open-webui -- curl -s http://ollama:11434/api/tags