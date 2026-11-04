# Self-Checkout Management (Django)

Painel administrativo web para o sistema Self-Checkout (Java Swing + MySQL). Partilha a base `self_checkout`
com a aplicação Java, sem a modificar.

## Decisões técnicas (baseadas no `schema.sql`)

| Tabela | Colunas | Notas |
|---|---|---|
| `customer` | `uuid` (PK), `name`, `balance` | |
| `product` | `uuid` (PK), `name`, `price`, `stock`, `minimum_stock` | **tem stock** → gestão de stock e alertas implementados |
| `sale` | `id` (PK), `customer_uuid` (FK), `sale_date`, `total` | |
| `sale_item` | `id`, `sale_id` (FK), `product_uuid` (FK), `quantity`, `unit_price`, `subtotal` | |
| `payment` | `id`, `sale_id` (FK), `amount`, `payment_method` | |

* Todos os models são `managed = False`; **nenhuma migration é aplicada à base MySQL partilhada** (o router em
  `config/db_router.py` bloqueia-o). As tabelas existentes não são alteradas.
* Utilizadores, sessões e auditoria ficam numa **base interna separada** (`default`): SQLite por omissão
  (`admin_data.sqlite3`) ou outro schema MySQL (`ADMIN_DB_ENGINE=mysql`). Assim não é criada nenhuma tabela nova na base do Java.
* Vendas, itens de venda e pagamentos são **só de leitura** (o model lança `PermissionError` em `save/delete`; a API só expõe GET).
* O saldo do cliente só pode ser definido ao criar; não é editável depois (é gerido pela app Java), nem via API.
* Clientes/produtos com vendas associadas **não podem ser eliminados** (as FKs existem no MySQL).
* Os métodos de pagamento no filtro vêm dos valores existentes na tabela `payment`.

### Limitações da estrutura actual
* `payment` não tem **estado** nem **data** → a data mostrada é a da venda associada; não há "estado da transacção".
* Não existe data de registo de clientes/produtos nem histórico de movimentos de stock.
* Não há categorias de produto nem utilizadores/operadores no schema Java.
Qualquer extensão (ex.: coluna `status` em `payment`) exige a tua autorização prévia — não foi feita nenhuma.

## Instalação

```bash
python -m venv venv && source venv/bin/activate        # Windows: venv\Scripts\activate
# mysqlclient precisa de libs do sistema (Ubuntu: sudo apt install libmysqlclient-dev pkg-config build-essential)
pip install -r requirements.txt
cp .env.example .env                                   # preencher SECRET_KEY, DB_USER, DB_PASSWORD
python manage.py check_db                              # testa a ligação ao MySQL 192.168.10.44 e compara colunas
python manage.py migrate                               # cria só a base INTERNA (utilizadores, sessões, auditoria)
python manage.py setup_roles                           # grupos Administrador / Operador
python manage.py createsuperuser                       # o superuser é Administrador
python manage.py runserver
```

Abrir http://127.0.0.1:8000/ . Criar operadores em *Utilizadores*.
**Nunca** corras `migrate --database selfcheckout` (o router recusa-o de qualquer forma).

O utilizador MySQL precisa de SELECT em todas as tabelas e INSERT/UPDATE/DELETE em `customer` e `product`.
Bootstrap, Bootstrap Icons e Chart.js são carregados por CDN (jsDelivr).

## Perfis
* **Administrador** (ou superuser): tudo, incluindo relatórios, auditoria, utilizadores e escrita em clientes/produtos.
* **Operador**: consulta de dashboard, clientes, produtos, vendas e pagamentos.

## API REST (`/api/`, sessão ou HTTP Basic)
`customers/` e `products/` (GET, POST, PUT/PATCH, DELETE por `uuid`; escrita só Administrador, com `?search=`),
`sales/` e `sales/{id}/` (filtros `customer`, `date_from`, `date_to`), `payments/` (`method`), `dashboard/statistics/`.
Conflitos de integridade devolvem 409. Todas as escritas ficam na auditoria.

## Testes
`python manage.py test` — corre em SQLite em memória (nunca toca no MySQL real) e cobre permissões, CRUD, auditoria,
dashboard, filtros, relatórios (Excel/PDF) e API.
Antes de produção valida a compatibilidade com a app Java contra uma cópia da base.

## Estrutura
`config/` · `apps/{core,accounts,audit,customers,products,sales,payments,dashboard,reports,api}` · `templates/` · `static/` · `tests/`
