# Telegram Promo Filter

Bot para filtrar mensagens de canais de promoções do Telegram com base em palavras-chave específicas e enviar a mensagem da promo para o WhatsApp.  

## Funcionalidades

- Filtra mensagens de **vários canais de promo do Telegram**.
- Procura por **palavras-chave específicas** definidas pelo usuário.
- Envia a mensagem filtrada para o **WhatsApp** quando alguma palavra-chave é encontrada.
- Configuração simples por comandos no Telegram
- Bot online 24/7

## Comandos (Telegram)
  - `/l`: Lista todas as palavras que estão sendo ouvidas no momento. Ex:  
    ```markdown
    /l
    
    Lista de itens:
    1. PS5
    2. B650M
    3. Ryzen 5
    ```
  - `/a <palavra>`: Adiciona uma nova palavra a lista. Ex:
    ```
    Lista de itens:
    1. PS5
    2. B650M
    3. Ryzen 5
    
    /a RTX 5090
    
    Lista de itens:
    1. PS5
    2. B650M
    3. Ryzen 5
    4. RTX 5090
    ```
  - `/r <numero>`: Remove uma nova palavra da lista informando o número. Ex:
    ```
    Lista de itens:
    1. Monitor AOC 27
    2. RTX 3060
    3. Playstation 5
    
    /r 2
    
    Lista de itens:
    1. Monitor AOC 27
    2. Playstation 5
    ```
    
## TODO
  - Enviar comandos pelo próprio whatsapp
  - Poder adicionar/remover os canais de promo para ouvir a lista
  - Apos 30m de nenhuma mensagem em nenhum canal o bot entra em stand-by e reinicia quando uma nova mensagem chega, perdendo o state (palavras salvas)
  - Logs 