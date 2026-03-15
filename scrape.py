import requests
from bs4 import BeautifulSoup
import csv

url = 'https://www.quanthockey.com/nhl/records/nhl-players-all-time-points-leaders.html'

response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

table = soup.find('table', class_='ps_tbl')
if not table:
    print("Table not found")
    exit()

rows = table.find_all('tr')[2:]  # Skip header rows

data = []
for row in rows[:50]:  # Top 50
    cols = row.find_all('td')
    if len(cols) < 12:
        continue
    rk = cols[0].text.strip()
    country = cols[1].text.strip() or (cols[1].find('img')['alt'] if cols[1].find('img') else 'Unknown')
    name = cols[2].text.strip()
    team = cols[3].text.strip()
    dob = cols[4].text.strip()
    position = cols[5].text.strip()
    gp = cols[6].text.strip()
    g = cols[7].text.strip()
    a = cols[8].text.strip()
    p = cols[9].text.strip()
    pim = cols[10].text.strip()
    plus_minus = cols[11].text.strip()
    data.append([country, name, team, dob, position, gp, g, a, p, pim, plus_minus])

with open('top50_stats.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Country of Origin', 'Name', 'Team', 'DOB', 'Position', 'GP', 'G', 'A', 'P', 'PIM', '+/-'])
    writer.writerows(data)

print("CSV created: top50_stats.csv")