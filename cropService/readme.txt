
ТРРП 4 лаба 
сервис для обрезки изображений по координатам

для функционирования нужно задать переменную среды TRRP4_CROP_ADDR, например 
TRRP4_CROP_ADDR=127.0.0.1:8181

для подготовки сборки docker образа
CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main .  
docker build -t crop_service_trrp4 -f Dockerfile.scratch .