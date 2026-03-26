from app.models.wildfire import predict as wildfire_predict
from app.models.flood import predict as flood_predict
from app.models.cyclone import predict as cyclone_predict
from app.models.earthquake import predict as earthquake_predict
from app.models.landslide import predict as landslide_predict

PREDICTORS = {
    "wildfire": wildfire_predict,
    "flood": flood_predict,
    "cyclone": cyclone_predict,
    "earthquake": earthquake_predict,
    "landslide": landslide_predict,
}
