
kubectl apply -f ollama.yaml
kubectl delete -f ollama.yaml

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

====================================================