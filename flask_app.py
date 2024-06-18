from flask import Flask, jsonify, render_template
from flask_pymongo import PyMongo
import pandas as pd
from datetime import datetime

app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb+srv://osder:78575353@cluster0.jdqqlsg.mongodb.net/vet_cristo?retryWrites=true&w=majority&appName=Cluster0"
mongo = PyMongo(app)

@app.route('/api/report')
def report():
    try:
        visits = mongo.db.visits.find()
        df = pd.DataFrame(list(visits))
        df['date'] = pd.to_datetime(df['date'])
        df_completado = df[df['status'] == 'Atendido']
        reservas_por_dia = df_completado[df_completado['reserved'] == True].groupby(df_completado['date'].dt.date).size()
        sin_reserva_por_dia = df_completado[df_completado['reserved'] == False].groupby(df_completado['date'].dt.date).size()


        df_resumen = pd.DataFrame({
            'Reservas': reservas_por_dia,
            'Sin Reserva': sin_reserva_por_dia
        }).fillna(0)
        df_resumen.index = pd.to_datetime(df_resumen.index)
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



