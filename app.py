from flask import Flask, jsonify, render_template
from flask_pymongo import PyMongo
import pandas as pd
from dotenv import load_dotenv
import os

# Cargar variables de entorno desde el archivo .env
load_dotenv()

app = Flask(__name__)

# Configurar la conexión con MongoDB utilizando variables de entorno
MONGO_URI = f"mongodb+srv://{os.getenv('MONGO_USERNAME')}:{os.getenv('MONGO_PASSWORD')}@{os.getenv('MONGO_CLUSTER')}/{os.getenv('MONGO_DBNAME')}?retryWrites=true&w=majority&appName={os.getenv('MONGO_APPNAME')}"
app.config["MONGO_URI"] = MONGO_URI

mongo = PyMongo(app)

@app.route('/api/report', methods=['GET'])
def report():
    try:
        # Consultar la colección "visits"
        visita = mongo.db.visits.find()

        # Convertir a DataFrame
        df = pd.DataFrame(list(visita))

        # Convertir la columna de fecha a tipo datetime
        df['date'] = pd.to_datetime(df['date'])

        # Filtrar las atenciones completadas
        df_completado = df[df['status'] == 'Atendido']

        # Contar las reservas y atenciones sin cita por día
        reservas_por_dia = df_completado[df_completado['reserved'] == True].groupby(df_completado['date'].dt.date).size()
        sin_reserva_por_dia = df_completado[df_completado['reserved'] == False].groupby(df_completado['date'].dt.date).size()

        # Crear un DataFrame con las dos series
        df_resumen = pd.DataFrame({
            'Reservas': reservas_por_dia,
            'Sin Reserva': sin_reserva_por_dia
        }).fillna(0)

        # Asegurarse de que el índice del DataFrame es de tipo datetime
        df_resumen.index = pd.to_datetime(df_resumen.index)

        # Convertir los datos a un diccionario para JSON
        data = {
            'fechas': df_resumen.index.strftime('%Y-%m-%d').tolist(),
            'reservas': df_resumen['Reservas'].tolist(),
            'sinReserva': df_resumen['Sin Reserva'].tolist()
        }

        return jsonify(data)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
