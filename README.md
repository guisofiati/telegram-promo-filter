# Telegram Promo Filter

Um aplicativo para filtrar mensagens de canais de promoções do Telegram com base em palavras-chave específicas e enviar a promo para o WhatsApp pessoal.  

## Funcionalidades

- Filtra mensagens de **vários canais do Telegram**.
- Procura por **palavras-chave específicas** definidas pelo usuário.
- Envia mensagens para o **WhatsApp** quando alguma palavra-chave é encontrada.
- Configuração simples de **palavras e canais**.
- Atualmente rodando localmente.

## Estrutura do Projeto

- **utils/constantes.ts**  
  Contém duas listas principais:
  - `WORDS_TO_SEARCH`: lista de palavras-chave que serão monitoradas.  
    ```py
    WORDS_TO_SEARCH = ['PLAYSTATION 5', 'XBOX', 'B650M'];
    ```
  - `CHANNELS_ALLOWED`: lista de canais do Telegram que o app irá monitorar. Obs: Não é necesário colocar @ dos canais
    ```py
    CHANNELS_ALLOWED = ['@canal1', '@canal2', '@canal3'];
    ```

- **Evento da mensagem**  
  O app escuta mensagens dos canais permitidos e, caso alguma palavra da lista seja encontrada, dispara a notificação para o WhatsApp.

## TODO: como usar