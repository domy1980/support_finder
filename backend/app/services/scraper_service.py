import aiohttp
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import re
from urllib.parse import quote_plus
import time
import random

class ScraperService:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
        }
    
    async def search_web(self, query: str, engine: str = 'google') -> List[Dict[str, str]]:
        """Web検索を実行して結果を返す"""
        try:
            # Googleの検索URL
            search_url = f"https://www.google.com/search?q={quote_plus(query)}&hl=ja"
            
            # 通常のrequestsを使用（非同期の問題を回避）
            response = requests.get(search_url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                results = self._parse_search_results(response.text, engine)
                print(f"Found {len(results)} results for query: {query}")
                return results
            else:
                print(f"Search failed with status code: {response.status_code}")
                return []
            
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def _parse_search_results(self, html: str, engine: str) -> List[Dict[str, str]]:
        """検索結果をパース"""
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        if engine == 'google':
            # Google検索結果の要素を探す
            search_results = soup.find_all('div', class_='g')
            
            for result in search_results[:10]:  # 上位10件
                try:
                    # タイトルを取得
                    title_elem = result.find('h3')
                    if not title_elem:
                        continue
                    title = title_elem.get_text()
                    
                    # URLを取得
                    link_elem = result.find('a')
                    if not link_elem or not link_elem.get('href'):
                        continue
                    url = link_elem['href']
                    
                    # スニペットを取得
                    snippet_elem = result.find('div', class_=['VwiC3b', 'yXK7lf'])
                    snippet = snippet_elem.get_text() if snippet_elem else ""
                    
                    # 有効なURLのみを追加
                    if url.startswith('http'):
                        results.append({
                            'title': title,
                            'url': url,
                            'snippet': snippet
                        })
                except Exception as e:
                    print(f"Error parsing result: {e}")
                    continue
        
        return results
    
    async def fetch_page_content(self, url: str) -> Dict[str, Any]:
        """ウェブページの内容を取得"""
        try:
            # 通常のrequestsを使用
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                html = response.text
                soup = BeautifulSoup(html, 'html.parser')
                
                # スクリプトとスタイルを除去
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # テキストを抽出
                text = soup.get_text()
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = ' '.join(chunk for chunk in chunks if chunk)
                
                # タイトルを取得
                title = soup.title.string if soup.title else ""
                
                return {
                    'url': url,
                    'title': title,
                    'text': text[:5000],  # 最初の5000文字のみ
                    'success': True
                }
            else:
                return {'url': url, 'success': False, 'error': f'Status: {response.status_code}'}
        except Exception as e:
            return {'url': url, 'success': False, 'error': str(e)}
