# Publicacao gratuita no GitHub Pages

## Objetivo

Compartilhar o Assistente da Secretaria com professores e alunos, sem custo, para receber criticas e sugestoes.

## Arquivos principais

- `index.html`: pagina publica do assistente.
- `styles.css`: visual da pagina.
- `app.js`: busca local que funciona sem servidor Python.
- `data/base_conhecimento.json`: respostas revisadas.
- `data/setores.json`: setores, responsaveis e e-mails.
- `data/site_pages.json`: indice coletado do site oficial.

## Passo a passo no GitHub

1. Acesse https://github.com/new.
2. Crie um repositorio publico chamado `robo-assistente-ifsp-avare`.
3. Envie os arquivos do projeto para a branch `main`.
4. Abra `Settings > Pages`.
5. Em `Build and deployment`, escolha `Deploy from a branch`.
6. Em `Branch`, selecione `main` e `/root`.
7. Salve e aguarde o GitHub gerar o link publico.

## Forma mais simples de enviar

Use o arquivo `robo-assistente-ifsp-avare.zip`, que esta na raiz do projeto. Ele contem a versao pronta do commit atual.

## Coleta de sugestoes

Crie um Google Forms com perguntas como:

- Qual pergunta voce fez?
- O assistente respondeu corretamente?
- A resposta estava clara?
- Faltou algum setor, horario, documento ou link?
- Qual sugestao voce deixaria para melhorar?

Depois coloque o link do formulario no README do GitHub e, em um proximo passo, tambem dentro da tela do assistente.
