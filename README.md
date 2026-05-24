# Robo Assistente da Secretaria - IFSP Avare

Este projeto e o inicio do "cerebro" de uma robo/totem de atendimento para apoiar estudantes, servidores e visitantes com informacoes da vida academica e administrativa do IFSP Avare.

## Objetivo

Construir uma assistente capaz de responder perguntas sobre:

- locais e setores do campus;
- horarios de atendimento;
- responsaveis por areas e coordenadorias;
- emails institucionais e canais oficiais;
- procedimentos academicos comuns;
- calendario, documentos e orientacoes gerais;
- encaminhamento correto: "com quem eu falo sobre isso?".

## Fase atual

A fase atual e um MVP sem IA generativa. Ele usa uma base de conhecimento estruturada em `data/base_conhecimento.json` e um buscador simples em `src/brain.py`.

Isso permite validar o conteudo antes de adicionar voz, tela, avatar ou LLM online.

## Como testar

No terminal, dentro desta pasta:

```bash
python3 src/brain.py "qual o horario da secretaria?"
python3 src/brain.py "preciso de declaracao de matricula"
python3 src/brain.py "onde fica a assistencia estudantil?"
```

## Como abrir a interface

No terminal, dentro desta pasta:

```bash
python3 src/server.py
```

Depois acesse:

```text
http://127.0.0.1:8765
```

## Como compartilhar sem custo

O projeto tambem tem uma versao estatica pronta para GitHub Pages. Ela usa os arquivos `index.html`, `styles.css`, `app.js` e os JSONs da pasta `data/`, sem precisar de servidor Python.

Passos no GitHub:

1. Criar um repositorio publico.
2. Enviar estes arquivos para a branch `main`.
3. Em `Settings > Pages`, publicar a partir da branch `main` e da pasta `/root`.
4. Compartilhar o link gerado pelo GitHub Pages com professores e alunos.

Para sugestoes e criticas, o caminho mais simples e criar um Google Forms e colocar o link na descricao do repositorio ou na propria pagina do assistente.

## Proximos passos

1. Preencher a base com dados reais e revisados por setores do campus.
2. Criar perguntas frequentes por tema.
3. Adicionar interface web simples para uso em uma tela touch.
4. Adicionar painel administrativo para atualizacao dos dados.
5. Conectar um LLM usando a base oficial como fonte de verdade.
