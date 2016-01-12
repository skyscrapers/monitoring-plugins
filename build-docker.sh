docker build -t skyscrapers/monitoring-plugins .
docker run -v $(pwd):/src skyscrapers/monitoring-plugins