import requests
import json
import os
import random
from datetime import datetime

EMBY_CONFIG = {
    "server": "https://play.roarzone.net",
    "username": "roarzone_guest",
    "password": "",
    "deviceId": "1e58531d-f79d-420e-8d1f-275900e30433"
}

def format_date(date_str):
    if not date_str:
        return ""
    try:
        dt = datetime.strptime(date_str[:10], "%Y-%m-%d")
        return dt.strftime("%d %b %Y")
    except Exception:
        return date_str

def fetch_ott_data():
    main_url = "https://allinonedev.top/main1.json"
    folder_name = "wak_tu"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    try:
        response = requests.get(main_url, timeout=15)
        main_data = response.json()
        if "ott_platforms" in main_data:
            for platform in main_data["ott_platforms"]:
                p_name = platform.get("name")
                p_logo = platform.get("logo")
                p_adult = platform.get("adult", "no")
                p_premium = platform.get("premium", "no")
                json_url = platform.get("json_url")
                file_save_name = p_name.replace(" ", "_")
                print(f"Mandamina OTT: {p_name}")
                try:
                    p_response = requests.get(json_url, timeout=15)
                    content_data = p_response.json()
                    if "categories" in content_data:
                        for category in content_data["categories"]:
                            category["name"] = p_name
                            category["logo"] = p_logo
                            category["adult"] = p_adult
                            category["premium"] = p_premium
                    filename = os.path.join(folder_name, f"{file_save_name}.json")
                    with open(filename, "w", encoding="utf-8") as f:
                        json.dump(content_data, f, indent=2, ensure_ascii=False)
                except Exception as e:
                    print(f"Hadisoana tamin'ny OTT {p_name}: {e}")
    except Exception as e:
        print(f"Hadisoana tamin'ny fakana config: {e}")

def fetch_emby_movies(parent_id, platform_name, save_filename):
    folder_name = "wak_tu"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    print(f"Mandamina Emby: {platform_name} (ID: {parent_id})")
    
    auth_url = f"{EMBY_CONFIG['server']}/emby/Users/AuthenticateByName"
    auth_header = f'MediaBrowser Client="Emby Web", Device="GitHub Action", DeviceId="{EMBY_CONFIG["deviceId"]}", Version="4.9.1.80"'
    payload = {"Username": EMBY_CONFIG['username'], "Pw": EMBY_CONFIG['password']}
    headers = {"Content-Type": "application/json", "X-Emby-Authorization": auth_header}
    
    try:
        auth_res = requests.post(auth_url, json=payload, headers=headers, timeout=15, verify=False)
        auth_data = auth_res.json()
        
        if "AccessToken" in auth_data:
            token = auth_data["AccessToken"]
            user_id = auth_data["SessionInfo"]["UserId"]
            items_url = f"{EMBY_CONFIG['server']}/emby/Users/{user_id}/Items"
            
            params = {
                "ParentId": parent_id,
                "Recursive": "true",
                "IncludeItemTypes": "Movie",
                "Fields": "PrimaryImageTag,ProductionYear,CommunityRating,Genres,Overview,People,PremiereDate,BackdropImageTags,VoteCount",
                "api_key": token
            }
            
            items_res = requests.get(items_url, params=params, timeout=20, verify=False)
            items_data = items_res.json()
            
            if "Items" in items_data:
                all_items = []
                for item in items_data["Items"]:
                    m_id = item["Id"]
                    
                    director = ""
                    if "People" in item:
                        for person in item["People"]:
                            if person.get("Type") == "Director":
                                director = person.get("Name")
                                break
                    
                    slider_url = ""
                    if item.get("BackdropImageTags"):
                        slider_url = f"{EMBY_CONFIG['server']}/emby/Items/{m_id}/Images/Backdrop/0?quality=90&api_key={token}"
                    
                    raw_rating = item.get("CommunityRating", 0.0)
                    formatted_rating = f"{float(raw_rating):.1f}"
                    
                    if raw_rating <= 0:
                        auto_votes = random.randint(50, 200)
                    else:
                        auto_votes = int(float(raw_rating) * 1250) + random.randint(100, 999)
                    
                    year = item.get("ProductionYear")
                    if year:
                        display_title = f"{item['Name']} ({year})"
                    else:
                        display_title = item["Name"]
                    
                    movie_obj = {
                        "category": platform_name,
                        "director": director,
                        "genre": item.get("Genres", []),
                        "imdbRating": formatted_rating,
                        "imdbVotes": auto_votes,
                        "language": "Hindi",
                        "posterUrl": f"{EMBY_CONFIG['server']}/emby/Items/{m_id}/Images/Primary?quality=90&api_key={token}",
                        "releaseDate": format_date(item.get("PremiereDate")),
                        "sliderUrl": slider_url,
                        "status": "on",
                        "storyline": item.get("Overview", ""),
                        "streamUrl": f"{EMBY_CONFIG['server']}/emby/Videos/{m_id}/stream?static=true&api_key={token}",
                        "title": display_title,
                        "headers": {
                            "referer": f"{EMBY_CONFIG['server']}/",
                            "origin": "",
                            "user_agent": ""
                        }
                    }
                    all_items.append(movie_obj)
                
                db_path = os.path.join(folder_name, save_filename)
                with open(db_path, "w", encoding="utf-8") as f:
                    json.dump(all_items, f, indent=2, ensure_ascii=False)
                
                print(f"Fahombiazana: sarimihetsika {len(all_items)} voatahiry ao amin'ny {db_path}")
        else:
            print(f"Tsy nahomby ny fidirana ho an'ny {platform_name}")
    except Exception as e:
        print(f"Hadisoana ho an'ny {platform_name}: {e}")

if __name__ == "__main__":
    fetch_ott_data()
    fetch_emby_movies("3", "Bollywood", "db.json")
    fetch_emby_movies("7660", "South India", "db2.json")
    fetch_emby_movies("9031", "Hollywood", "db3.json")
    fetch_emby_movies("137971", "Kolkata", "db4.json")
    fetch_emby_movies("137931", "Bangla", "db5.json")
