# REST-API-Project

Este é um projeto simples de uma REST API para pagamentos hipotéticos usando Flask (Python) e SQLAlchemy. 

A API suporta dois métodos de pagamento: boleto e cartão de crédito. Caso o método de pagamento seja boleto, gera como resposta o código numérico do boleto.
Caso seja cartão de crédito, gera como resposta um processamento hipotético do cartão de crédito e diz se o pagamento foi ou não bem-sucedido.

Para realizar um pagamento, é necessário que o usuário esteja logado numa conta válida que esteja na base de dados. Cada usuário pode ser ou admin ou um
usuário comum.

Além de realizar pagamentos, os usuários podem realizar outras ações específicas como visualizar os pagamentos feitos, visualizar apenas um pagamento 
específico, visualizar os usuários da base de dados, promover ou deletar usuários, mas tudo dependendo de seu cargo como usuário (admin ou não).

## Design da REST API

O projeto em si é simples. As ações principais são: conseguir logar na API e realizar pagamentos (seja em boleto ou cartão de crédito). A arquitetura e
o funcionamento da REST API em si está ilustrada na imagem abaixo. O cliente se comunica com a API enviando requisições HTTP (GET, POST, DELETE, PUT) com
os dados em formato JSON com as informações que deseja obter do banco de dados. A API atua como este intermediário entre o cliente e o banco de dados,
retornando as informações requisitadas em formato JSON e o código de status HTTP (200, 404) na resposta para o cliente.

![image](https://user-images.githubusercontent.com/53957365/163680015-27afb77b-35d1-4528-816e-c68a317fa8d9.png)

O projeto do banco de dados utilizado foi do tipo relacional. O banco de dados é o 'database.db', dentro dele há duas tabelas: 'user' e 'payment'.
A tabela 'user' guarda as informações do usuário (id, public_id, username, password, admin). Já a tabela 'payment' guarda as informações dos pagamentos
(id, user_id, name, cpf, email, payment_method,...). Essas duas tabelas se relacionam entre si através do 'id' do usuário.

Quando um pagamento é feito, ele é assinado com o 'user_id' do usuário que o realizou, isto é, o 'user_id' é a chave primária (valor único para
cada usuário) da tabela 'user' e na tabela 'payment' ela é usada como chave estrangeira. Abaixo há um Diagrama ER para melhor explicar o modelo.

![image](https://user-images.githubusercontent.com/53957365/163731772-a45cea74-10ca-448e-9d82-171634a064a1.png)

- **Token de acesso**

  Uma parte importante do projeto são os *tokens* de acesso de usuário. Quando um login é feito, é gerado um *token* de acesso para o usuário logado.
  Este *token* será utilizado pela API para reconhecer o usuário e também reconhecer as permissões dele para executar as tarefas. Para acessar qualquer
  recurso da API, é necessário passar o **token** de acesso. Este tem uma validade de 15 minutos, após expirar é necessário logar novamente.
  
  ![image](https://user-images.githubusercontent.com/53957365/163736769-93e78fc3-5690-4dae-b357-cbec6cff0ec3.png)


## Recursos da API

1. **Efetuar pagamentos.**
2. **Visualizar todos os pagamentos feitos pelo cliente logado.** *(Admins podem ver os pagamentos de todos os usuários)*
3. **Visualizar todos os clientes da base de dados.** *(Apenas admins)*
4. **Criar um novo cliente.** *(Apenas admins)*
5. **Promover um cliente à admin.** *(Apenas admins)*
6. **Deletar um cliente.** *(Apenas admins)*
7. **Visualizar informações de um cliente específico.** *(Apenas admins)*
8. **Deletar um pagamento.** *(O cliente logado pode deletar apenas pagamentos feitos por ele mesmo, admins podem deletar pagamentos de qualquer cliente)*
9. **Visualizar informações de um pagamento específico.** *(Cliente visualiza um de seus próprios pagamentos, admins visualizam qualquer pagamento)*

## Rodando a API

Para rodar a API, primeiro é necessário clonar todo o repositório para a sua máquina. Assumindo que você esteja usando uma máquina Linux, digite o comando:

```
git clone https://github.com/leoandrade20/REST-API-Project.git
```

Com isso, é necessário instalar as bibliotecas do Python para o projeto. Você pode escolher instalar tudo na sua máquina ou em uma máquina virtual
do próprio Python (*virtualenv*). Deixarei abaixo ambos os métodos.

- **Instalando o *virtualenv*, ativando a máquina virtual e instalando os pacotes requeridos.**

  Na pasta principal do projeto (REST-API-Project), digite os seguintes comandos.

  ```
  cd REST-API-Project
  pip install virtualenv
  virtualenv [nome da máquina virtual]
  source [nome da máquina virtual]/bin/activate
  ```
  
  Os comandos acima irão instalar o virtualenv, criar uma máquina virtual com ele e ativá-la. Nomeie a máquina virtual como quiser. 
  Agora, você pode digitar o seguinte comando e instalará os pacotes necessários na máquina virtual criada. 
  
  ```
  python3 -m pip install -r requirements.txt
  ```
  
  Caso queira instalar os pacotes diretamente na sua máquina, basta digitar o comando acima direto sem fazer o processo da *virtualenv*.
  
  Para desativar a máquina virtual após o uso, digite:
  
  ```
  deactivate
  ```
  
- **Inicializando o banco de dados**

  Temos um banco de dados chamado "database.db". Ele é criado e acessado utilizando o SQLAlchemy. Para iniciar o banco de dados, dentro da pasta **app**   acesse o console Pythone digite os seguintes comandos:

  ```
  cd app
  python3
  from app import db
  db.create_all()
  exit()
  ```
  
  Dessa forma a base de dados foi inicializada!
  
- **Rodando a API**
 
   Para rodar a API em si, ainda na pasta **app**, basta digitar o seguinte comando (caso esteja utilizando uma versão do Python 3.X.X)
   
   ```
   python3 app.py
   ```
   
   Se você executou o código, a API já está rodando na sua máquina na porta 5000, ou seja, endereço **http://localhost:5000** ! 
   
   ![image](https://user-images.githubusercontent.com/53957365/163655328-b0c013a1-157b-4a3f-8048-c05e36bdd781.png)
   
   ![image](https://user-images.githubusercontent.com/53957365/163655512-fe879d27-e892-4145-8355-bd7eaab49a11.png)

## Testando a API

Agora, vamos testar os recursos da API. O cURL será a ferramenta majoritariamente utilizada para consumir a API acessando os endpoints.
Na base de dados "database.db" já estão incluídos dois usuários: {"username": "admin", "password": "1234"} e  {"username": "edward", "password": "newgate"}.

- **Logando na API.**

  Abra uma nova aba no seu terminal de comandos. O usuário 'admin' já possui o cargo de admin por padrão. Mas primeiro vamos logar com o usuário 'edward' para testar alguns recursos. Para logar digite:

  ```
  curl -i -X GET -H "Content-Type: application/json" --user edward:newgate http://localhost:5000/login  
  ```

  ![image](https://user-images.githubusercontent.com/53957365/163655885-d9941cb9-ebf9-4486-98a9-cd65c83d9ec3.png)


  Na imagem acima podemos ver a resposta da API com o token de acesso para o usuário logado em questão, no caso, o 'edward'. Este token de acesso é um
  pré-requisito para acessar qualquer recurso da API. De agora em diante, para qualquer recurso que utilizarmos, vamos passar o token de acesso no 
  cabeçalho próprio que é o 'X-Access-Token'.

  Antes de efetuar um pagamento, vamos consultar se já há algum pagamento feito pelo usuário 'edward'. Para ilustrar como os dados devem ser passados, já 
  deixei alguns dados prontos no banco de dados. Para consultar, basta digitar:

- **Visualizando os pagamentos do usuário logado.**

  ```
  curl -i -X GET -H "Content-Type: application/json" -H "X-Access-Token: [insira o token do usuario edward aqui]" http://localhost:5000/payment
  ```

  Você irá visualizar a seguinte resposta da API (tela do lado esquerdo) com as informações dos pagamentos já feitos pelo usuário 'edward'. 
  O token de  acesso é mudado a cada sessão de login e também possui um tempo de expiração de 15 minutos.

  ![image](https://user-images.githubusercontent.com/53957365/163656529-47370283-00e0-46eb-94be-5a559781610d.png)
  
  Podemos ver que há dois pagamentos cadastrados no nome de Edward Newgate, um em boleto e o outro em cartão de crédito (com informações sobre este).
  
- **Efetuando um pagamento em boleto.**  
  
  Vamos efetuar um novo pagamento em boleto. Devemos passar para API neste caso o nome, email, CPF e quantia a pagar. 
  Um exemplo de código para passar essas informações:
  
  ```
  curl -i -X POST -H "Content-Type: application/json" -H "X-Access-Token: [insira o token do usuario edward aqui]" -d '{"name": "Edward Newgate", "email": "shirohige@gmail", "cpf": "01203412755", "amount": 50550, "payment_method": 0}' http://localhost:5000
  ```
  
  ![image](https://user-images.githubusercontent.com/53957365/163658713-d4f9ae86-9c81-4286-b98d-541d71a54ca4.png)
  
  O 'payment_method = 0' indica que o método de pagamento é em boleto.
  
  E, como esperado, retornou o código numérico do boleto a ser pago.
  
- **Efetuando um pagamento com cartão de crédito.**
  
  Para efetuar um pagamento usando o cartão de crédito, além de passar as informações sobre o cliente (nome, email, cpf), a quantia e o método 
  de pagamento, precisamos também passar os dados do cartão, ou seja, o nome no cartão, o número do cartão, a validade e código de segurança (CVV).
  
  Para efetuar um pagamento desse tipo, digite o seguinte comando abaixo:
  
  ```
  curl -i -X POST -H "Content-Type: application/json" -H "X-Access-Token: [insira o token do usuário edward aqui]" -d '{"name": "Edward Newgate", "email": "shirohige@gmail.com", "cpf": "01203412755", "amount": 12400000, "payment_method": 1, "name_card": "EDWARD NEWGATE", "num_card": "1112333544467778", "expiration": "04/25", "cvv": 700}' http://localhost:5000/payment
  ```
  
  ![image](https://user-images.githubusercontent.com/53957365/163658780-e4a9ac62-1928-48da-91a1-706daeeb7521.png)
  
  O 'payment_method = 1' indica que o método de pagamento é com cartão de crédito.
  
  Note que fiz duas requisições e que uma retornou a mensagem com "Pagamento bem-sucedido!" e a outra com "Cartão de crédito inválido". A única coisa
  que mudou nas requisições foi a quantia a ser paga, mas isso não tem nada a ver com o processamento do cartão. Na verdade, como foi dito no início,
  o cartão não é processado, a resposta se o pagamento foi bem-sucedido ou não é aleatório. 
  Com isso, esperamos que apenas que a primeira requisição bem-sucedida tenha tido os dados do pagamento e do cartão armazenados no banco de dados.
  
- **Verificando se os pagamentos foram armazenados no banco de dados.**
  
  Para verificar se os pagamentos no nome do usuario 'edward' foram armazenados na base de dados e assinalados com o respectivo 'user_id', vamos 
  consultar o banco de dados ainda logados com a conta do 'edward' (usando o token deste usuário). Digitamos novamente o comando:
  
  ```
  curl -i -X GET -H "Content-Type: application/json" -H "X-Access-Token: [insira o token do usuario edward aqui]" http://localhost:5000/payment
  ```
  
  ![image](https://user-images.githubusercontent.com/53957365/163658995-23fec003-13e0-4cc9-a337-0fbbd966bd02.png)
  
  Observe que os dois pagamentos, um em boleto e o outro em cartão que passamos para API, foram armazenados.
  Note que o 'user_id' de todos os pagamentos é o mesmo, que se refere ao usuário 'edward'.
  
  Apenas para verificarmos que os dados estão persistindo de verdade, podemos consultar o banco de dados diretamente utilizando a ferramenta
  *sqlite3*.
  
  ![image](https://user-images.githubusercontent.com/53957365/163659206-11709778-111c-4829-ac3e-df69c19d9556.png)
  
  Apesar de não ser a melhor das formas de visualizar essa tabela no banco de dados, podemos observar em nome de quem os pagamentos foram feitos,
  o 'user_id' do cliente, o método de pagamento (0 ou 1), o email, cpf.

- **Logando como admin e visualizando os usuários no banco de dados.**
  
  Vamos brevemente logar como admin apenas para consultar as informações sobre os usuários no banco de dados (caso você tente fazer essa consulta
  logado com o usuário 'edward', não conseguirá porque ele não tem permissão para isso). Digite o comando:
  
  ```
  curl -i -X GET -H "Content-Type: application/json" --user admin:1234 http://localhost:5000/login
  ```
  
  ![image](https://user-images.githubusercontent.com/53957365/163680607-fbc91983-3887-48f9-9115-1da96d4ea234.png)
  
  Observe que cada usuário tem seu próprio 'public_id'. Note também que estamos guardando as hashs das senhas no banco de dados.
  
  Como 'admin', podemos visualizar também as informações de um usuário específico passando o seu 'public_id'.
  
  ```
  curl -i -X GET -H "Content-Type: application/json" -H "X-Access-Token: [insira o token do usuario admin aqui]" http://localhost:5000/user/[insira o  public_id do usuário desejado aqui]
  ```
  
  ![image](https://user-images.githubusercontent.com/53957365/163680662-1f8ab78e-94dd-4aa0-ab99-bd7679305510.png)

## Funcionalidades extras

A principal atividade neste projeto era construir uma API onde um cliente pudesse acessá-la e efetuar pagamentos. As demais funcionalidades adicionadas, como visualizar todos os pagamentos, criar um usuário novo, promover e deletar usuários, tudo isso são funções extras que não fazem parte da ideia do projeto em si mas foram exploradas para melhor entender o conceito de banco de dados relacionais e também das requisições à uma REST API.

- **Criar um novo usuário (somente admins)**

  ```
  curl -i -X POST -H "Content-Type: application/json" -H "X-Access-Token: [insira o token do usuário admin aqui]" -d '{"username": "eren", "password": "yeager"}' http://localhost:5000/user
  ```
  
- **Promover um usuário a admin (somente admins)**

  ```
  curl -i -X PUT -H "Content-Type: application/json" -H "X-Access-Token: [insira o token do usuário admin aqui]" http://localhost:5000/user/[insira o public_id do usuário a ser promovido aqui]
  ```
  
- **Deletar um usuário (somente admins)**
  
  ```
  curl -i -X DELETE -H "Content-Type: application/json" -H "X-Access-Token: [insira o token do usuário admin aqui]" http://localhost:5000/user/[insira o public_id do usuário a ser promovido aqui]
  ```
- **Visualizar informações de um cliente específico. (somente admins)**

  ```
  curl -i -X GET -H "Content-Type: application/json" -H "X-Access-Token: [insira o token do usuário admin aqui]" http://localhost:5000/user/[insira o public_id do usuário aqui]
  ```
  
- **Visualizar informações de um pagamento específico. (usuário comum visualiza apenas seus próprios pagamentos, admins visualizam qualquer um)**

  ```
  curl -i -X GET -H "Content-Type: application/json" -H "X-Access-Token: [insira o token do usuário admin aqui]" http://localhost:5000/payment/[insira o payment_id do pagamento aqui]
  ```

## **Referências**

- Canal "Pretty Printed": https://www.youtube.com/watch?v=WxGBoY5iNXY

A base do projeto foi este tutorial, pude reaproveitar o código, adaptar e adicionar mais funcionalidades para este projeto. 
Também não utilizei o Postman para fazer as requisições, e sim o cURL.
