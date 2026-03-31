# LoL Patch Watcher 🕵️🤖

Um bot de Discord inteligente que monitora automaticamente as atualizações do League of Legends e notifica os canais configurados sobre quais campeões foram **buffados**, **nerfados** ou **ajustados**.

## ✨ Funcionalidades

- **Monitoramento Automático**: Verifica novas versões do Data Dragon a cada 30 minutos (configurável).
- **Análise Inteligente**: Compara atributos base (HP, Armadura, etc.) entre a versão atual e a anterior.
- **Classificação Visual**: Envia embeds coloridos e intuitivos:
  - 🟩 **Verde**: Buffs
  - 🟥 **Vermelho**: Nerfs
  - 🟦 **Azul**: Ajustes
- **Configuração Simples**: Use `/setup` em qualquer servidor para definir o canal de notificações.

## 🛠️ Tecnologias Utilizadas

- **Python 3.11+**
- **discord.py**: Interface com a API do Discord.
- **Riot Watcher**: Auxílio na integração com dados da Riot.
- **SQLAlchemy (Async)** + **SQLite**: Persistência de configurações e histórico de patches.
- **BeautifulSoup4**: Scraping das notas de patch oficiais.

## 🚀 Como Rodar

### Pré-requisitos
- Python 3.11 ou Docker.
- Token de Bot do Discord (obtido no [Discord Developer Portal](https://discord.com/developers/applications)).
- API Key da Riot Games (obtida no [Riot Developer Portal](https://developer.riotgames.com/)).

### Instalação Local

1.  Clone o repositório.
2.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```
3.  Renomeie o arquivo `.env.example` para `.env` e preencha suas chaves:
    ```env
    DISCORD_TOKEN=seu_token_aqui
    RIOT_API_KEY=sua_chave_riot_aqui
    ```
4.  Inicie o bot:
    ```bash
    python -m bot.main
    ```

### Rodando com Docker

```bash
docker-compose up -d
```

## 🎮 Comandos Slash

- `/setup [canal]`: Define o canal para envio automático das atualizações (Requer Admin).
- `/status`: Verifica se o bot está operante.
- `/lastpatch`: Exibe informações sobre a última atualização processada.

---
Desenvolvido com ❤️ para a comunidade de League of Legends.
