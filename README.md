# REST-API-Project

Este é um projeto simples de uma REST API para pagamentos hipotéticos usando Flask (Python) e SQLAlchemy. 

A API suporta dois métodos de pagamento: boleto e cartão de crédito. Caso o método de pagamento seja boleto, gera como resposta o código numérico do boleto.
Caso seja cartão de crédito, gera como resposta um processamento hipotético do cartão de crédito e diz se o pagamento foi ou não bem-sucedido.

Para realizar um pagamento, é necessário que o usuário esteja logado numa conta válida que esteja na base de dados. Cada usuário pode ser ou admin ou um
usuário comum.

Além de realizar pagamentos, os usuários podem realizar outras ações específicas como visualizar os pagamentos feitos, visualizar apenas um pagamento 
específico, visualizar os usuários da base de dados, promover ou deletar usuários, mas tudo dependendo de seu cargo como usuário (admin ou não).

## Rodando a API

Para rodar a API, primeiro é necessário clonar todo o repositório para a sua máquina. Assumindo que você esteja usando uma máquina Linux, digite o comando:

```
git clone https://github.com/leoandrade20/REST-API-Project.git
```

Com isso, é necessário instalar as bibliotecas do Python para o projeto. Você pode escolher instalar tudo na sua máquina ou em uma máquina virtual
do próprio Python (*virtualenv*). Deixarei abaixo ambos os métodos.

- Instalando o *virtualenv* e ativando a máquina virtual.

  ```
  pip install virtualenv
  virtualenv [nome da máquina virtual]
  ```

