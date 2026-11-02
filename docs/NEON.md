# Banco de dados PostgreSQL no Neon

O sistema usa **SQLite** quando não existe a variável `DATABASE_URL` (desenvolvimento e testes)
e **PostgreSQL** quando ela existe (produção no Neon).

## 1. Criar o banco
1. Crie a conta em neon.com e um **projeto** (se houver, escolha a região de São Paulo).
2. Em **Connect**, copie a *connection string* (`postgresql://usuario:senha@...neon.tech/banco?sslmode=require`).
   Prefira a versão **pooled** (host com `-pooler`).
3. **Nunca** coloque essa string no código nem no GitHub: ela contém a senha.

## 2. Testar no seu computador contra o Neon
```powershell
$env:DATABASE_URL = "COLE_AQUI_A_CONNECTION_STRING"
pip install -r requirements.txt
flask --app wsgi run --debug
```
Abra http://127.0.0.1:5000/api/saude?db=1 — deve responder `"banco": "postgres"`.
As tabelas são criadas sozinhas na primeira conexão. Para voltar ao SQLite, feche o terminal
ou rode `Remove-Item Env:DATABASE_URL`.

## 3. Teste de integração (opcional, recomendado)
Crie uma **branch** de teste no Neon (Branches > New branch) e use a string dela:
```powershell
$env:TEST_DATABASE_URL = "STRING_DA_BRANCH_DE_TESTE"
python -m unittest tests.test_db -v
```
O teste remove apenas os registros que ele mesmo criou.

## 4. Publicar no Render
No painel do serviço: **Environment > Add Environment Variable** → `DATABASE_URL` = a string do Neon.

## 5. Cota gratuita
O plano gratuito do Neon suspende o banco após 5 minutos sem uso e acorda sozinho (o primeiro
acesso pode demorar um pouco). A rota `/api/saude` não consulta o banco de propósito, para que
os testes de saúde do Render não mantenham o banco acordado e gastem as horas gratuitas.
Faça uma exportação dos dados antes da banca: não conte com backup no plano gratuito.
