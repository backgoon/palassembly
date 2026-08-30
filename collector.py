import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# 국회 입법예고 진행중 목록 URL
URL = "https://pal.assembly.go.kr/napal/lgslt/lgsltpa/list.do"

def fetch_top10_bills():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    bills = []
    
    try:
        response = requests.get(URL, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 목록 테이블의 모든 행(row) 탐색
        rows = soup.select('table tbody tr')
        
        for row in rows:
            cols = row.select('td')
            if len(cols) < 3:
                continue
                
            # 링크 태그 추출
            title_tag = row.select_one('a')
            if not title_tag:
                continue
                
            title = title_tag.text.strip()
            href = title_tag.get('href', '')
            
            # 절대 경로 변환
            if href.startswith('/'):
                link = "https://pal.assembly.go.kr" + href
            elif href.startswith('http'):
                link = href
            else:
                link = "https://pal.assembly.go.kr/napal/lgslt/lgsltpa/" + href
                
            # 컬럼 수가 다양할 수 있으므로 안전하게 추출
            proposer = cols[2].text.strip() if len(cols) > 2 else "-"
            period = cols[-1].text.strip() if len(cols) > 3 else "-"
            
            bills.append({
                'title': title,
                'proposer': proposer,
                'period': period,
                'link': link
            })
            
            # 최상단 10개만 수집
            if len(bills) >= 10:
                break
                
    except Exception as e:
        print(f"입법예고 목록 수집 중 오류 발생: {e}")

    return bills

def create_mobile_html(bills):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>국회 입법예고 모니터링 (테스트)</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f7; margin: 0; padding: 15px; color: #333; }}
        .header {{ background: #1c1c1e; color: #fff; padding: 20px; border-radius: 12px; margin-bottom: 15px; }}
        .header h1 {{ margin: 0 0 5px 0; font-size: 20px; }}
        .header p {{ margin: 0; font-size: 12px; color: #aaa; }}
        .card {{ background: #fff; padding: 16px; border-radius: 12px; margin-bottom: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }}
        .card h3 {{ margin: 0 0 10px 0; font-size: 16px; color: #111; line-height: 1.4; }}
        .info {{ font-size: 13px; color: #666; margin-bottom: 6px; }}
        .btn {{ display: block; width: 100%; padding: 12px 0; background: #007aff; color: #fff; text-align: center; border-radius: 8px; text-decoration: none; font-weight: bold; margin-top: 10px; font-size: 14px; box-sizing: border-box; }}
        .empty {{ text-align: center; padding: 40px 20px; color: #888; background: #fff; border-radius: 12px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🏛️ 국회 입법예고 최신 10건 (테스트)</h1>
        <p>최근 업데이트: {now} (KST)</p>
    </div>
"""

    if not bills:
        html_content += '<div class="empty"><p>입법예고 목록을 불러오지 못했습니다.</p></div>'
    else:
        for bill in bills:
            html_content += f"""
    <div class="card">
        <h3>{bill['title']}</h3>
        <div class="info">👤 <b>발의자/선출:</b> {bill['proposer']}</div>
        <div class="info">📅 <b>예고기간:</b> {bill['period']}</div>
        <a href="{bill['link']}" target="_blank" class="btn">국회 입법예고 상세보기 ➡️</a>
    </div>
"""

    html_content += """
</body>
</html>
"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == '__main__':
    bills = fetch_top10_bills()
    print(f"수집된 최신 법안 수: {len(bills)}")
    create_mobile_html(bills)
