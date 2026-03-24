from rocca_app import create_app, db

app = create_app()

with app.app_context():
    print('Iniciando a criacao das novas tabelas no banco de dados...')
    try:
        # Cria as tabelas do SQLAlchemy que nao existem ainda
        db.create_all()
        print('Todas as tabelas foram sincronizadas/criadas com sucesso!')
    except Exception as e:
        print(f'Erro ao criar as tabelas: {e}')
