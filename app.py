from flask import Flask, jsonify
from watering_controller import check_and_water
from sensor import read_soil_moisture

app = Flask(__name__)

@app.route('/moisture')
def moisture_status():
    moisture_level = read_soil_moisture()
    return jsonify({"soil_moisture": moisture_level})

@app.route('/water')
def water_plants():
    check_and_water()
    return "Watering process initiated"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
