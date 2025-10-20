# Скрипт для парсинга вакансий HH.ru
# Автор: [твое имя], 2025
# Цель: Сбор вакансий по аналитике данных для анализа рынка труда

...
# 💾 Данные сохраняются в data/hh_data_analyst.csv
import requests
import pandas as pd
import time
from tqdm import tqdm
from bs4 import BeautifulSoup

# Ключевые слова для поиска
KEYWORDS = [
    "аналитик данных", "data analyst", "аналитик", "BI аналитик",
    "data аналитик", "продуктовый аналитик", "business analyst",
    "Power BI", "Tableau", "SQL аналитик", "анализ данных"
]
# Скрипт для парсинга вакансий HH.ru
# Автор: [твое имя], 2025
# Цель: Сбор вакансий по аналитике данных для анализа рынка труда

...
# 💾 Данные сохраняются в data/hh_data_analyst.csv
# Фильтрация по ключевым навыкам
FILTER_SKILLS = ["sql", "excel", "bi", "python"]

# Результаты сохраняем сюда
RESULT_FILE = "hh_data_analyst.csv"

def get_vacancies(text):
    url = "https://api.hh.ru/vacancies"
    params = {
        "text": text,
        "area": 113,  # Россия
        "per_page": 100,
        "page": 0
    }
    vacancies = []
    while True:
        response = requests.get(url, params=params)
        data = response.json()
        vacancies.extend(data["items"])
        if data["pages"] - 1 == params["page"]:
            break
        params["page"] += 1
        time.sleep(0.2)
    return vacancies

def get_vacancy_details(vacancy_id):
    url = f"https://api.hh.ru/vacancies/{vacancy_id}"
    response = requests.get(url)
    return response.json()

def clean_text(text):
    if not text:
        return ""
    soup = BeautifulSoup(text, "html.parser")
    clean = soup.get_text(separator=" ").lower().strip()
    clean = " ".join(clean.split())
    return clean

def main():
    all_vacancies = []
    print("🔍 Получаем список вакансий...")
    seen_ids = set()

    # Получаем вакансии по каждому ключевому слову
    for kw in KEYWORDS:
        for v in get_vacancies(kw):
            if v["id"] not in seen_ids:
                seen_ids.add(v["id"])
                all_vacancies.append(v)

    print(f"📥 Найдено {len(all_vacancies)} уникальных вакансий")
    details = []

    for v in tqdm(all_vacancies, desc="Загружаем детали"):
        vacancy_data = get_vacancy_details(v["id"])
        description = clean_text(vacancy_data.get("description"))
        employer = vacancy_data.get("employer", {}).get("name", "")
        specialization = (
            vacancy_data.get("specializations")[0]["name"]
            if vacancy_data.get("specializations") else ""
        )
        industry = (
            vacancy_data.get("employer", {}).get("industries")[0]["name"]
            if vacancy_data.get("employer", {}).get("industries") else ""
        )
        salary = vacancy_data.get("salary")
        salary_from = salary.get("from") if salary else None
        salary_to = salary.get("to") if salary else None

        # Фильтрация по навыкам
        if any(skill in description for skill in FILTER_SKILLS):
            details.append({
                "id": vacancy_data["id"],
                "name": vacancy_data.get("name", ""),
                "employer": employer,
                "specialization": specialization,
                "industry": industry,
                "description": description,
                "salary_from": salary_from,
                "salary_to": salary_to,
                "published_at": vacancy_data.get("published_at")
            })

        time.sleep(0.2)

    print(f"✅ Отобрано {len(details)} вакансий после фильтрации")
    df = pd.DataFrame(details)
    df.to_csv(RESULT_FILE, index=False, encoding="utf-8-sig")
    print(f"💾 Данные сохранены в {RESULT_FILE}")

if __name__ == "__main__":
    main()