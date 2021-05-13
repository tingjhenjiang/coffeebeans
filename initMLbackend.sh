#label-studio start coffeebeansML --ml-backends http://0.0.0.0:9090 --port 8083
cd label-studio-ml-backend
rm my_ml_backend -r
label-studio-ml init my_ml_backend --script ../labelstudio_ml_backend_cfbmodel.py --force
label-studio-ml start my_ml_backend

