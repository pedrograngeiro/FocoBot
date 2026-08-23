# FocoBot

![FocoBot](./%F0%9F%A4%96FocoBot.png)

Bot Pomodoro para Discord: 25 minutos de foco, pausas de 5 minutos e uma pausa
longa de 10 minutos a cada quatro rodadas.

## Requisitos

- Python 3.10 ou mais recente
- [FFmpeg](https://ffmpeg.org/download.html) disponível no `PATH`
- Uma aplicação/bot criada no [Discord Developer Portal](https://discord.com/developers/applications)
- Permissões para ler e enviar mensagens e para conectar e falar em canais de voz

## Configuração

1. Crie e ative um ambiente virtual:

   ```bash
   python -m venv .venv
   # Windows (PowerShell)
   .venv\Scripts\Activate.ps1
   # Linux/macOS
   source .venv/bin/activate
   ```

2. Instale as dependências:

   ```bash
   python -m pip install -r requirements.txt
   ```

3. Copie `.env.example` para `.env` e informe o token do bot:

   ```dotenv
   BOT_TOKEN=seu_token_aqui
   ```

4. No Developer Portal, em **Bot > Privileged Gateway Intents**, habilite
   **Message Content Intent**. Ele é necessário porque o FocoBot preserva os
   comandos tradicionais com prefixo `!`.

   Em **Installation**, mantenha também o escopo `applications.commands` para
   que os comandos de barra sejam registrados.

5. Inicie o bot a partir da raiz do projeto:

   ```bash
   python -m FocoBot
   ```

## Comandos

- `/comecar`, `!começar`, `!comecar` ou `!foco`: inicia os ciclos no canal de voz atual
- `!parar`: interrompe o ciclo sem zerar as rodadas
- `!encerrar`: interrompe o ciclo e zera as rodadas
- `!pausar`: congela a etapa e preserva o tempo restante
- `!retomar`: continua uma etapa pausada
- `!pular`: avança para a próxima etapa do ciclo
- `!tempo`: mostra etapa, estado, tempo restante e tempo decorrido
- `!ajuda`: lista os comandos disponíveis

Todos os comandos canônicos acima também estão disponíveis com `/`. Na primeira
execução após uma atualização, o Discord pode levar alguns minutos para exibir
os comandos globais de barra.

## Desenvolvimento

Execute os testes com:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest
ruff check .
```

O código foi migrado da API 1.7 do `discord.py` para a API assíncrona 2.x. Os
comandos antigos foram mantidos, portanto o rollback consiste em restaurar a
versão anterior do código e do `requirements.txt`; não há migração de dados.
