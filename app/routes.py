from flask import Blueprint, render_template, request, jsonify, current_app, redirect, url_for
from datetime import datetime
import pytz
import requests
from .utils import get_db_connection
from dotenv import load_dotenv
import os

# Cargar variables de entorno desde .env
load_dotenv()

# Define el blueprint principal
main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    """
    Muestra el formulario de tokenización y guarda student_id, payor_id, session_id y recipient_id.
    """
    if request.method == 'POST':
        # Captura el Student ID enviado desde el formulario
        student_id = request.form.get('student_id')

        # Configuración de Flywire
        flywire_api_url = current_app.config['FLYWIRE_API_URL']
        flywire_api_key = current_app.config['FLYWIRE_API_KEY']
        recipient_id = os.getenv('RECIPIENT_ID')

        # Validar que el RECIPIENT_ID esté definido
        if not recipient_id:
            raise ValueError("El RECIPIENT_ID no está definido en el archivo .env")

        # Generar la fecha y hora actual en el huso horario de México
        mexico_tz = pytz.timezone('America/Mexico_City')
        transaction_datetime = datetime.now(mexico_tz).strftime('%Y-%m-%d %H:%M:%S')

        # Cuerpo del payload para Flywire
        payload = {
            "type": "tokenization",
            "charge_intent": {
                "mode": "unscheduled"
            },
            "options": {
                "form": {
                    "action_button": "save",
                    "locale": "en"
                }
            },
            "schema": "cards",
            "payor_id": student_id,
            "notifications_url": "https://example.com/notifications",
            "external_reference": "test_reference",
            "recipient_id": recipient_id
        }

        headers = {
            "X-AUTHENTICATION-Key": flywire_api_key,
            "Content-Type": "application/json"
        }

        try:
            # Llama a la API de Flywire
            response = requests.post(flywire_api_url, json=payload, headers=headers)
            response.raise_for_status()
            session_data = response.json()

            # Extrae el session_id y la URL del formulario
            session_id = session_data.get('id')
            hosted_form_url = session_data.get('hosted_form', {}).get('url')

            # Guarda el registro inicial en la base de datos
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO transactions (student_id, payor_id, session_id, recipient_id, transaction_datetime)
                VALUES (?, ?, ?, ?, ?)
                """,
                (student_id, student_id, session_id, recipient_id, transaction_datetime)
            )
            conn.commit()
            conn.close()

            # Renderiza la plantilla con la URL del formulario de Flywire
            return render_template('flywire_form.html', form_url=hosted_form_url)

        except requests.exceptions.RequestException:
            return jsonify({"message": "Error al iniciar tokenización"}), 500

    return render_template('form.html')

@main.route('/confirm', methods=['POST'])
def confirm_session():
    """
    Procesa la confirmación de una sesión de Flywire y actualiza los datos en la base de datos.
    """
    session_id = request.json.get('session_id')
    if not session_id:
        return jsonify({"error": "El session_id es requerido"}), 400

    # Configuración de Flywire
    confirm_url = current_app.config['FLYWIRE_CONFIRM_URL'].format(session_id=session_id)
    headers = {
        "X-AUTHENTICATION-Key": current_app.config['FLYWIRE_API_KEY'],
        "Content-Type": "application/json"
    }

    try:
        # Llama a la API para confirmar la sesión
        response = requests.post(confirm_url, headers=headers)
        response.raise_for_status()
        confirm_data = response.json()

        # Extraer datos del método de pago y del mandato
        payment_method = confirm_data.get('payment_method', {})
        mandate = confirm_data.get('mandate', {})

        if not payment_method or not mandate:
            return jsonify({"error": "Datos incompletos recibidos de Flywire"}), 400

        # Extraer información específica
        token = payment_method.get('token')
        mandate_id = mandate.get('id')
        payment_type = payment_method.get('type')
        brand = payment_method.get('brand')
        card_classification = payment_method.get('card_classification')
        card_expiration = payment_method.get('card_expiration')
        last_four_digits = payment_method.get('last_four_digits')
        country = payment_method.get('country')
        issuer = payment_method.get('issuer')

        # Validar datos esenciales
        if not token or not mandate_id:
            return jsonify({"error": "Faltan datos esenciales"}), 400

        # Obtener la fecha y hora actual en el huso horario de México
        mexico_tz = pytz.timezone('America/Mexico_City')
        transaction_datetime = datetime.now(mexico_tz).strftime('%Y-%m-%d %H:%M:%S')

        # Actualiza los datos en la base de datos usando el session_id
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE transactions
            SET token = ?, mandate = ?, payment_type = ?, brand = ?, card_classification = ?, 
                card_expiration = ?, last_four_digits = ?, country = ?, issuer = ?, transaction_datetime = ?
            WHERE session_id = ?
            """,
            (token, mandate_id, payment_type, brand, card_classification, card_expiration, 
             last_four_digits, country, issuer, transaction_datetime, session_id)
        )
        conn.commit()
        conn.close()

        # Redirige a la página de éxito
        return redirect(url_for('main.success_page'))

    except requests.exceptions.RequestException:
        return redirect(url_for('main.failure_page'))

@main.route('/success', methods=['GET'])
def success_page():
    """
    Página de éxito después de una tokenización exitosa.
    """
    return render_template('success.html')

@main.route('/failure', methods=['GET'])
def failure_page():
    """
    Página de fallo si ocurre un error en la tokenización.
    """
    return render_template('failure.html')

@main.cli.command("init-db")
def initialize_db():
    """
    Comando CLI para inicializar la base de datos.
    """
    from .utils import init_db
    init_db()
