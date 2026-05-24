# Testes de Busca e Acentuação

Data: 2026-05-24

Objetivo: verificar se perguntas sem acento encontram as mesmas respostas que perguntas com acento.

## Resultado

A normalização está funcionando. O cérebro remove acentos antes de comparar palavras, então perguntas como `mecanica` e `mecânica` chegam ao mesmo tipo de resposta.

## Casos testados

| Pergunta | Resultado |
|---|---|
| calendario academico | calendario-academico |
| calendário acadêmico | calendario-academico |
| estagios | estagio |
| estágios | estagio |
| mecanica | cursos-tecnicos-concomitantes |
| mecânica | cursos-tecnicos-concomitantes |
| mecatronica | cursos-tecnicos-integrados |
| mecatrônica | cursos-tecnicos-integrados |
| declaracao de matricula | declaracao-matricula |
| declaração de matrícula | declaracao-matricula |
| auxilio permanencia | assistencia-estudantil |
| auxílio permanência | assistencia-estudantil |
| gestao de pessoas | setor-cgp |
| gestão de pessoas | setor-cgp |
| licitacoes e contratos | setor-clt |
| licitações e contratos | setor-clt |
| horario de aulas mecatronica | horarios-de-aulas |
| horário de aulas mecatrônica | horarios-de-aulas |

## Fallback esperado

Uma pergunta inventada sem relação com a base caiu corretamente na resposta padrão:

- `xyz assunto inventado sem base` -> `nao-encontrado`

