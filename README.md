# Mercado Inteligente

MVP web para apoiar o controle de estoque e o acompanhamento da validade de alimentos no Mercado Rubi.

## Objetivo
Organizar o cadastro de produtos, registrar lotes e movimentações de entrada/saída e destacar lotes vencidos ou próximos do vencimento, contribuindo para a redução do desperdício.

## Escopo do MVP
- Cadastro e consulta de produtos.
- Registro de lotes por produto, com quantidade e datas.
- Registro de entradas e saídas de estoque.
- Consulta de lotes vencidos e próximos do vencimento.

## Tecnologias
- Python 3.12+
- FastAPI
- SQLAlchemy
- SQLite
- Jinja2
- HTML, CSS e JavaScript

## Como executar
1. Crie e ative um ambiente virtual.
2. Instale as dependências: `pip install -r requirements.txt`.
3. Inicie a aplicação: `uvicorn app.main:app --reload`.
4. Acesse `http://127.0.0.1:8000`.

O banco SQLite é criado automaticamente na primeira execução. Os dados de demonstração devem ser inseridos pela interface.

## Estrutura
- `app/`: aplicação, persistência, modelos, rotas e serviços.
- `app/templates/`: páginas HTML renderizadas com Jinja2.
- `app/static/`: estilos e recursos estáticos.

## Observação
Este é um MVP acadêmico. Utilize somente dados fictícios ou autorizados para demonstração; não inclua dados pessoais ou informações confidenciais do estabelecimento.
