# Importa feedparser para analisar feeds RSS do Reddit
import feedparser
# Importa httpx para fazer requisições HTTP assíncronas (mais eficiente que requests)
import httpx
# Importa datetime para trabalhar com datas e horários
from datetime import datetime
# Importa logger para registrar eventos e erros durante a execução
from loguru import logger
# Importa a conexão com o banco de dados MongoDB
from ...database import db

# Define a classe RedditRSSCollector que é responsável por coletar posts do Reddit
class RedditRSSCollector:
    # Método assíncrono que coleta posts de um subreddit específico
    # Parâmetros:
    # - subreddit: nome do subreddit a ser monitorado (ex: "technology")
    # - brand: nome da marca que está sendo monitorada (para categorização)
    async def collect(self, subreddit: str, brand: str):
        # Constrói a URL do feed RSS do subreddit ordenado por posts mais recentes
        # Formato: https://www.reddit.com/r/{nome_do_subreddit}/new/.rss
        url = f"https://www.reddit.com/r/{subreddit}/new/.rss"

        # Define cabeçalhos HTTP para a requisição
        headers = {
            # User-Agent simula um navegador Chrome para evitar bloqueios do Reddit
            # Muitos sites bloqueiam requisições sem User-Agent ou com User-Agents suspeitos
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }

        # Cria um cliente HTTP assíncrono usando context manager (garante fechamento automático)
        async with httpx.AsyncClient() as client:
            # Faz uma requisição GET assíncrona para o feed RSS do Reddit
            # await pausa a execução até receber a resposta, permitindo outras tarefas executarem
            response = await client.get(url, headers=headers)

        # Analisa o conteúdo XML/RSS da resposta usando feedparser
        # Transforma o XML em um objeto Python fácil de manipular
        feed = feedparser.parse(response.text)

        # Itera sobre cada entrada (post) encontrada no feed RSS
        for entry in feed.entries[:50]:  # Limita a 50 posts para evitar sobrecarga
            # Cria um dicionário com os dados da menção/post
            mention = {
                # Define a fonte como "reddit" para identificar de onde veio os dados
                "source": "reddit",
                # Armazena o nome da marca sendo monitorada
                "brand": brand,
                # ID único do post no Reddit (usado para evitar duplicatas)
                "external_id": entry.id,
                # Título do post
                "title": entry.title,
                # Conteúdo/descrição do post (resumo)
                "content": entry.summary,
                # URL completa do post no Reddit
                "url": entry.link,
                # Timestamp de quando o dado foi coletado (hora UTC para padronização)
                "created_at": datetime.utcnow(),
                # Flag indicando se o post já foi processado pela análise de sentimento
                "is_processed": False
            }
        
        # Atualiza ou insere (upsert) o documento no MongoDB
        # update_one é usado de forma assíncrona para não bloquear a execução
        await db.mentions.update_one(
            # Filtro: busca por documentos com mesmo external_id e source
            # Isso evita duplicação de posts no banco de dados
            {"external_id": mention["external_id"], "source": "reddit"},
            # $set: operador MongoDB que atualiza os campos com novos valores
            {"$set": mention },
            # upsert=True: se não encontrar documento existente, cria um novo
            # Isso garante que sempre teremos os dados mais recentes
            upsert=True
        )