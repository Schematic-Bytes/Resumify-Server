
apt-get update && apt-get install  build-essential libpoppler-cpp-dev pkg-config libpoppler-dev -y

pip install -r requirements.txt


if [[ $(hostname) = "web" ]]; then
    uvicorn src.app:app --host 0.0.0.0 --port 5000
elif [[ $(hostname) = "worker" ]]; then
    celery --app=src worker -l INFO
fi