import requests
import json
import time

API_KEY = "89dc647004be44c785266ccd4d69576a"
catalog = []

def fetch_category(endpoint, pages, cat_type, extra_params={}):
    items = []
    print(f"\n🔄 Récupération des {cat_type} ({pages} pages)...")
    
    for page in range(1, pages + 1):
        params = {
            "api_key": API_KEY,
            "language": "fr-FR",
            "page": page,
            **extra_params
        }
        
        try:
            r = requests.get(f"https://api.themoviedb.org/3/{endpoint}", params=params, timeout=10)
            data = r.json()
            
            if "results" not in data:
                print(f"✗ Erreur page {page}: {data}")
                break
                
            for item in data["results"]:
                tmdb_id = item["id"]
                title = item.get("title") or item.get("name") or "Titre inconnu"
                date_str = item.get("release_date") or item.get("first_air_date") or ""
                year = date_str[:4] if date_str else "N/A"
                
                is_tv = (cat_type in ["séries", "animés"])
                frembed_url = f"https://frembed.casa/api/serie.php?id={tmdb_id}&sa=1&epi=1" if is_tv else f"https://frembed.casa/api/film.php?id={tmdb_id}"
                
                items.append({
                    "type": "tv" if is_tv else "movie",
                    "imdb_id": f"tmdb_{tmdb_id}",
                    "tmdb_id_clean": tmdb_id,
                    "title": title,
                    "year": year,
                    "rating": item.get("vote_average", 0),
                    "poster": f"https://image.tmdb.org/t/p/w342{item['poster_path']}" if item.get("poster_path") else "",
                    "overview": item.get("overview", ""),
                    "vf_sources": {
                        "frembed": frembed_url
                    },
                    "vf_direct": frembed_url
                })
                
            print(f"✓ {cat_type.capitalize()} Page {page}/{pages} - Total cumulé : {len(items)}")
            time.sleep(0.15)
            
        except Exception as e:
            print(f"❌ Erreur sur la page {page} : {e}")
            break
            
    return items

# 1. 1500 Films (75 pages x 20)
movies = fetch_category("movie/popular", 75, "films")

# 2. 2000 Séries (100 pages x 20)
series = fetch_category("tv/popular", 100, "séries")

# 3. 1000 Animés (50 pages x 20 - Genre Animation + Origine JP)
animes = fetch_category("discover/tv", 50, "animés", {
    "with_genres": "16",
    "with_original_language": "ja",
    "sort_by": "popularity.desc"
})

# Fusion et suppression des doublons
seen_ids = set()
for item in (movies + series + animes):
    key = f"{item['type']}_{item['tmdb_id_clean']}"
    if key not in seen_ids:
        seen_ids.add(key)
        catalog.append(item)

# Sauvegarde dans data.json et public/data.json si le dossier existe
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(catalog, f, ensure_ascii=False, indent=2)

try:
    with open("public/data.json", "w", encoding="utf-8") as f:
        json.dump(catalog, f, ensure_ascii=False, indent=2)
except:
    pass

print(f"\n✅ Terminé ! {len(catalog)} contenus enregistrés dans data.json")