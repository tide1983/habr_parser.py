import time
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

# Определяем список ключевых слов:
KEYWORDS = ['дизайн', 'фото', 'web', 'python']

# Базовый URL
BASE_URL = 'https://habr.com'
ARTICLES_URL = f'{BASE_URL}/ru/all/'

def get_articles_from_page(url):
    """Получает статьи с указанной страницы"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all('article')
    return articles

def parse_article_preview(article):
    """Парсит preview информацию из статьи"""
    try:
        # Заголовок
        title_element = article.find('h2').find('a') or article.find('h3').find('a')
        title = title_element.text.strip()
        link = title_element.get('href')
        if link and not link.startswith('http'):
            link = BASE_URL + link
        
        # Дата публикации
        time_element = article.find('time')
        date = time_element.get('datetime') if time_element else ''
        
        # Preview текст (заголовок + текст превью)
        preview_text = title.lower()
        
        # Ищем текст превью
        preview_div = article.find('div', class_=re.compile('article-formatted-body'))
        if preview_div:
            preview_text += ' ' + preview_div.get_text(strip=True).lower()
        
        return {
            'date': date,
            'title': title,
            'link': link,
            'preview_text': preview_text
        }
    except Exception:
        return None

def check_keywords_in_preview(preview_text, keywords):
    """Проверяет наличие ключевых слов в preview"""
    found_keywords = []
    for keyword in keywords:
        if keyword.lower() in preview_text:
            found_keywords.append(keyword)
    return found_keywords

def main():
    try:
        articles = get_articles_from_page(ARTICLES_URL)
        found_articles = []
        
        for i, article in enumerate(articles):
            article_data = parse_article_preview(article)
            
            if not article_data:
                continue
                
            found_keywords = check_keywords_in_preview(article_data['preview_text'], KEYWORDS)
            
            if found_keywords:
                # Форматируем дату
                if article_data['date']:
                    try:
                        date_obj = datetime.fromisoformat(article_data['date'].replace('Z', '+00:00'))
                        formatted_date = date_obj.strftime('%d.%m.%Y')
                    except:
                        formatted_date = article_data['date']
                else:
                    formatted_date = "Дата не определена"
                
                found_articles.append({
                    'date': formatted_date,
                    'title': article_data['title'],
                    'link': article_data['link'],
                    'keywords': found_keywords
                })
            
            # ДОБАВЛЯЕМ ЗАДЕРЖКУ МЕЖДУ ОБРАБОТКОЙ СТАТЕЙ
            if i < len(articles) - 1:  # Не ждем после последней статьи
                time.sleep(1)  # Задержка 1 секунда
        
        # Вывод результатов в требуемом формате
        for article in found_articles:
            print(f"{article['date']} - {article['title']} - {article['link']}")
            
    except requests.RequestException as e:
        print(f"Ошибка при получении данных: {e}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    main()