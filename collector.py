import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# 시험용 집중 키워드 (차별, 평등, 불평등 관련)
KEYWORDS = ['차별', '평등', '불평등', '인권', '약자', '성별', '괴롭힘']

# 국회 입법예고 목록 URL
URL = "https://pal.assembly.go.kr/napal/lgslt/lgsltpa/list.do"

def fetch_bills():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    matched_bills = []
    
    # 키워드별로 직접 검색을 시도하여 목록 수집
    for search_kw in ['차별', '평등', '불평등', '인권']:
        params = {
            'searchCondition': '1', # 법률안명 검색
            'searchKeyword': search_kw
        }
        try:
            response = requests.get(URL, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            rows = soup.select('table.board_list tbody tr')
            for row in rows:
                cols = row.select('td')
                if len(cols) < 5:
                    continue
                    
                title_tag = row.select_one('a')
                if not title_tag:
                    continue
                    
                title = title_tag.text.strip()
                href = title_tag.get('href', '')
                
                # 링크 및 중복 체크
                link = "https://pal.assembly.go.kr" + href if href.startswith('/') else href
                proposer = cols[2].text.strip() if len(cols) > 2 else "-"
                period = cols[4].text.strip() if len(cols) > 4 else "-"
                
                # 중복 수집 방지
                if not any(b['title'] == title for b in matched_bills):
                    matched_bills.append({
                        'title': title,
                        'proposer': proposer,
                        'period': period,
                        'link': link
                    })
        except Exception as e:
            print(f"[{search_kw}] 검색 요청 중 오류 발생: {e}")

    return matched_bills

def create_mobile_html(bills):
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>국회 입법예고 모니터링</title>
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
        <h1>🏛️ 입법예고 모니터링 (시험 작동)</h1>
        <p>최근 업데이트: {now} (KST)</p>
    </div>
"""

    if not bills:
        html_content += '<div class="empty"><p>현재 진행 중인 입법예고 중 해당 검색어로 조회된 법안이 없습니다.</p></div>'
    else:
        for bill in bills:
            html_content += f"""
    <div class="card">
        <h3>{bill['title']}</h3>
        <div class="info">👤 <b>발의자:</b> {bill['proposer']}</div>
        <div class="info">📅 <b>예고기간:</b> {bill['period']}</div>
        <a href="{bill['link']}" target="_blank" class="btn">국회 입법예고 반대 의견 제출 ➡️</a>
    </div>
"""

    html_content += """
</body>
</html>
"""

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == '__main__':
    bills = fetch_bills()
    print(f"수집된 법안 수: {len(bills)}")
    create_mobile_html(bills)
