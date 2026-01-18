# Configuração da Google API Key

## Como obter sua API Key do Google Gemini

### 1. Acesse o Google AI Studio
- Vá para: https://makersuite.google.com/app/apikey
- Faça login com sua conta Google

### 2. Criar uma nova API Key
- Clique em "Create API Key"
- Escolha um projeto existente ou crie um novo
- Copie a API Key gerada

### 3. Configurar no projeto
- Abra o arquivo `.env` no seu projeto
- Substitua `your_google_api_key_here` pela sua chave real:

```env
GOOGLE_API_KEY=sua_chave_real_aqui
```

### 4. Testar a configuração
```bash
python -c "from src.ingest import get_embeddings; get_embeddings(); print('Configuração OK!')"
```

## Limites e Custos

- **Gratuito**: Até 15 requisições por minuto
- **Pago**: $0.0005 por 1K tokens para embeddings
- **Pago**: $0.0005 por 1K tokens para chat

## Troubleshooting

### Erro: "API key not valid"
- Verifique se a chave foi copiada corretamente
- Certifique-se de que não há espaços extras
- Confirme que a API Key está ativa no Google AI Studio

### Erro: "Quota exceeded"
- Você atingiu o limite de requisições
- Aguarde alguns minutos ou configure billing para limites maiores

### Erro: "Permission denied"
- Verifique se a API Key tem as permissões necessárias
- Certifique-se de que o projeto está ativo
