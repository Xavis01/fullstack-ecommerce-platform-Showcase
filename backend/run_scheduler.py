import sys
import os
from pathlib import Path
import time

# Adiciona a raiz do projeto ao sys.path para permitir imports de 'backend'
ROOT_DIR = Path(__file__).parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from backend.rocca_app import create_app
from backend.scheduler import scheduler, Config as SchedulerConfig

def main():
    print("Starting Scheduler...")
    app = create_app()
    
    # Carrega a configuração do Scheduler (JOBS) na app
    app.config.from_object(SchedulerConfig)
    
    # Inicializa o scheduler com a app context
    scheduler.init_app(app)
    scheduler.start()
    print("Scheduler started successfully.")
    
    try:
        # Mantém o processo rodando
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        print("Stopping scheduler...")
        scheduler.shutdown()

if __name__ == "__main__":
    main()
