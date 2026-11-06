# ADR 001 — Escopo executável e consistência

Status: implementado.

## Contexto

Um rollout não deveria avançar apenas porque uma média pontual parece aceitável; incerteza e reprodutibilidade fazem parte da decisão.

## Decisão

Bootstrap com seed fixa permite reproduzir a decisão sobre a mesma entrada. O limite inferior acima do guardrail recomenda rollback; limite superior dentro dele recomenda promote; intervalo cruzando o limiar recomenda hold. Menos de 20 amostras retorna insufficient_data.

## Alternativas e consequências

Um monólito modular reduz pontos de falha e mantém a demonstração reproduzível.
Microsserviços adicionariam rede, observabilidade distribuída e implantação sem necessidade comprovada.
SQLite reduz dependências, mas tem um escritor por vez. PostgreSQL é a evolução para concorrência sustentada.
A troca de banco exige revisão das transações e testes; não é apenas trocar a URL.

## Fronteiras de segurança

Credencial → identidade do tenant → caso de uso → SQL com filtro por tenant.
Não há header arbitrário de identidade. Credenciais locais existem somente para demonstração.
Documentação interativa e health são públicos; operações de negócio são autenticadas.

## Evolução

Ingerir métricas reais via OpenTelemetry/Prometheus; testar cobertura empírica do intervalo; introduzir block bootstrap para séries temporais, guardrails de erros e custo, política de aprovação humana e integração progressiva com controladores de rollout.
