# curl -X POST http://localhost:5000/predict_image_bytes -d '{img_bytes:@/Users/congvo/Documents/Screen Shot 2020-02-16 at 10.19.57 PM.png}'

curl --header "Content-Type: application/json" \
-X POST http://localhost:5000/predict_json -d '{"data":10}'

curl --header "Content-Type: application/json" \
-X GET http://localhost:5000/statistics