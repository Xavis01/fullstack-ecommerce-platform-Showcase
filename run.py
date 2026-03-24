# run.py
import os
from backend.rocca_app import create_app
from backend.scheduler import scheduler, Config

app = create_app()
app.config.from_object(Config)
scheduler.init_app(app)

if __name__ == "__main__":
    # Apenas inicia o scheduler no processo principal da aplicação
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        scheduler.start()
    # NUNCA rodar com debug=True em produção (expõe o debugger interativo do Werkzeug)
    flask_env = os.getenv("FLASK_ENV", "development")
    app.run(debug=(flask_env == "development"))
