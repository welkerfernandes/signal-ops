# Modelo, evidência e limitações

Bootstrap percentil da regressão relativa de média, 1.000 reamostragens, seed 42, mínimo de 20 observações por grupo e teto de 500. Trata-se de inferência estatística clássica; não há rede neural nem treinamento. Intervalos não são garantias para distribuições arbitrárias.

## Uso pretendido

Demonstração técnica e avaliação controlada com dados sintéticos. A execução é local e determinística.
Não existem métricas de produção ou benchmarks de desempenho declarados.

## Avaliação disponível

A suíte verifica comportamentos esperados, cenários adversos e invariantes. Isso não demonstra
generalização estatística em dados reais. Antes de adoção, defina um dataset independente,
critérios de aceitação, avaliação por segmento e revisão humana dos erros.

## Limitações do produto

É um motor consultivo de inferência estatística, não um controlador de Kubernetes nem um LLM. Pressupõe amostras representativas e aproximadamente independentes; não corrige viés, autocorrelação, testes repetidos ou sazonalidade. O p95 é descritivo e não determina a decisão. Não há ação automática em produção.
