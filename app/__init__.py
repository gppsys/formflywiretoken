from flask import Flask
from decouple import config
from .utils import init_db  # Importa init_db para definir el comando directamente


def create_app():
    """
    Fábrica de aplicaciones para inicializar la aplicación Flask.
    """
    app = Flask(__name__)

    # Configuración de base de datos desde .env
    app.config['DB_SERVER'] = config('DB_SERVER', default=r"localhost\SQLEXPRESS")
    app.config['DB_DATABASE'] = config('DB_DATABASE', default="FlywireDB")
    app.config['DB_USERNAME'] = config('DB_USERNAME', default="default_username")
    app.config['DB_PASSWORD'] = config('DB_PASSWORD', default="default_password")
    app.config['DB_DRIVER'] = config('DB_DRIVER', default="{ODBC Driver 17 for SQL Server}")

    # Configuración de Flywire API
    app.config['FLYWIRE_API_KEY'] = config('FLYWIRE_API_KEY', default="")
    app.config['FLYWIRE_API_URL'] = config('FLYWIRE_API_URL', default="")
    app.config['FLYWIRE_CONFIRM_URL'] = config('FLYWIRE_CONFIRM_URL', default="")

    # Configuración de certificados
    app.config['CERT_PATH'] = config('CERT_PATH', default="certs/cert.pem")
    app.config['KEY_PATH'] = config('KEY_PATH', default="certs/key.pem")

    # Registro del comando directamente
    @app.cli.command("init-db")
    def initialize_db():
        """
        Comando CLI para inicializar la base de datos.
        """
        try:
            init_db()  # Llama a la función init_db de utils.py
            print("Base de datos inicializada correctamente.")
        except Exception as e:
            print(f"Error al inicializar la base de datos: {e}")

    # Registro del blueprint principal
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Registro del cierre de conexiones de la base de datos
    from .utils import close_db_connection
    app.teardown_appcontext(close_db_connection)

    return app
