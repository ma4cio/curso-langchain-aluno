# Rate Limiter - Contador de Requisições

## Visão Geral

O sistema inclui um contador de requisições automático que respeita o limite de **15 requisições por minuto** do Google Gemini (plano gratuito).

## Como Funciona

### 1. Controle Automático
- **Verificação automática**: Antes de cada requisição à API
- **Espera inteligente**: Aguarda automaticamente quando o limite é atingido
- **Processamento em lotes**: Otimiza o uso da API durante a ingestão

### 2. Janela Deslizante
- **Janela de 60 segundos**: Conta requisições dos últimos 60 segundos
- **Reset automático**: Requisições antigas são removidas automaticamente
- **Thread-safe**: Funciona corretamente com múltiplas requisições simultâneas

## Funcionalidades

### Status em Tempo Real
```python
from src.rate_limiter import print_rate_limit_status

# Mostra status completo
print_rate_limit_status()
```

**Exemplo de saída:**
```
--- Status do Rate Limiter ---
Requisições atuais: 12/15
Requisições restantes: 3
Reset em: 23.4 segundos
Pode fazer requisição: Sim
---------------------------
```

### Verificação Manual
```python
from src.rate_limiter import check_rate_limit

# Verifica se pode fazer requisição
if check_rate_limit():
    print("Pode prosseguir")
else:
    print("Aguarde...")
```

### Informações Detalhadas
```python
from src.rate_limiter import get_rate_limit_status

status = get_rate_limit_status()
print(f"Restantes: {status['remaining_requests']}")
print(f"Reset em: {status['reset_time']} segundos")
```

## Integração nos Scripts

### 1. Ingestão (`ingest.py`)
- **Processamento em lotes**: 5 chunks por vez
- **Verificação por lote**: Checa rate limit antes de cada lote
- **Status final**: Mostra status após conclusão

### 2. Busca (`search.py`)
- **Verificação prévia**: Checa rate limit antes da busca
- **Status antes/depois**: Mostra status antes e depois da operação

### 3. Chat (`chat.py`)
- **Verificação por pergunta**: Checa rate limit antes de cada resposta
- **Comando especial**: Digite `status` para ver o status atual
- **Aguarda automaticamente**: Se limite atingido, aguarda e tenta novamente

## Comandos Especiais no Chat

### `status`
Mostra o status atual do rate limiter:
```
--- Status do Rate Limiter ---
Requisições atuais: 8/15
Requisições restantes: 7
Reset em: 45.2 segundos
Pode fazer requisição: Sim
---------------------------
```

### `sair`
Encerra o chat normalmente.

## Teste do Rate Limiter

Execute o script de teste para ver o rate limiter em ação:

```bash
python src/test_rate_limiter.py
```

**Opções de teste:**
1. **Teste básico**: 20 requisições rápidas
2. **Teste de espera**: 16 requisições para testar a espera
3. **Monitor**: Acompanha o status por 70 segundos
4. **Todos os testes**: Executa todos os testes

## Configuração

### Limites Padrão
- **Máximo**: 15 requisições
- **Janela**: 60 segundos
- **Configurável**: Pode ser alterado no código

### Personalização
```python
from src.rate_limiter import RateLimiter

# Criar rate limiter personalizado
custom_limiter = RateLimiter(
    max_requests=10,    # 10 requisições
    time_window=30      # por 30 segundos
)
```

## Troubleshooting

### "Rate limit excedido"
- **Normal**: O sistema aguarda automaticamente
- **Aguarde**: O contador reseta a cada minuto
- **Verifique**: Use `status` para ver o tempo restante

### Requisições muito lentas
- **Verifique**: Se há muitas requisições em andamento
- **Aguarde**: O rate limiter aguarda automaticamente
- **Otimize**: Use processamento em lotes para ingestão

### Status incorreto
- **Reinicie**: O contador é resetado a cada execução
- **Verifique**: Se há múltiplas instâncias rodando
- **Aguarde**: O contador se corrige automaticamente

## Benefícios

1. **Conformidade**: Respeita os limites da API do Google Gemini
2. **Automatização**: Não requer intervenção manual
3. **Eficiência**: Otimiza o uso da API
4. **Transparência**: Mostra status em tempo real
5. **Robustez**: Funciona com múltiplas requisições simultâneas
