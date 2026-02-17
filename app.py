import requests
import json
import os

EMBY_CONFIG = {
    "server": "https://play.roarzone.info",
    "username": "roarzone_guest",
    "password": "",
    "parentId": "1395",
    "deviceId": "1e58531d-f79d-420e-8d1f-275900e30433",
    "platform_name": "Hindi Movies",
    "platform_logo": "https://lh3.googleusercontent.com/Zf8BDyJwIg3sVzRopsN8eqkRKQPmHuPn1TdnpCpta3IKeB7Nxvjv9W3MzQEIFUD_lPw=h315"
}

def fetch_ott_data():
    main_url = "https://allinonedev.top/main1.json"
    folder_name = "wak_tu"
    
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    try:
        response = requests.get(main_url)
        main_data = response.json()
        
        if "ott_platforms" in main_data:
            for platform in main_data["ott_platforms"]:
                p_name = platform.get("name")
                p_logo = platform.get("logo")
                p_adult = platform.get("adult", "no")
                p_premium = platform.get("premium", "no")
                json_url = platform.get("json_url")
                
                file_save_name = p_name.replace(" ", "_")
                print(f"Processing OTT Platform: {p_name}")
                
                try:
                    p_response = requests.get(json_url)
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
                    print(f"Error: {e}")
    except Exception as e:
        print(f"Error: {e}")

def fetch_emby_movies():
    print(f"Processing Emby: {EMBY_CONFIG['platform_name']}")
    auth_url = f"{EMBY_CONFIG['server']}/emby/Users/AuthenticateByName"
    auth_header = f"MediaBrowser Client=\"Emby Web\", Device=\"GitHub Action\", DeviceId=\"{EMBY_CONFIG['deviceId']}\", Version=\"4.9.1.80\""
    
    payload = {"Username": EMBY_CONFIG['username'], "Pw": EMBY_CONFIG['password']}
    headers = {"Content-Type": "application/json", "X-Emby-Authorization": auth_header}

    try:
        auth_res = requests.post(auth_url, json=payload, headers=headers, timeout=15)
        auth_data = auth_res.json()
        
        if "AccessToken" in auth_data:
            token = auth_data["AccessToken"]
            user_id = auth_data["SessionInfo"]["UserId"]
            
            items_url = f"{EMBY_CONFIG['server']}/emby/Users/{user_id}/Items"
            params = {
                "ParentId": EMBY_CONFIG['parentId'],
                "Recursive": "true",
                "IncludeItemTypes": "Movie",
                "Fields": "PrimaryImageTag,ProductionYear",
                "api_key": token
            }
            
            items_res = requests.get(items_url, params=params, timeout=20)
            items_data = items_res.json()
            
            if "Items" in items_data:
                all_items = []
                for item in items_data["Items"]:
                    m_id = item["Id"]
                    all_items.append({
                        "id": item["Name"],
                        "title": item["Name"],
                        "poster": f"{EMBY_CONFIG['server']}/emby/Items/{m_id}/Images/Primary?quality=90&api_key={token}",
                        "stream_url": f"{EMBY_CONFIG['server']}/emby/Videos/{m_id}/stream?static=true&api_key={token}",
                        "headers": {
                            "Referer": f"{EMBY_CONFIG['server']}/"
                        }
                    })
                
                hero_list = all_items[:1]
                
                final_db = {
                    "hero": hero_list,
                    "categories": [
                        {
                            "name": EMBY_CONFIG['platform_name'],
                            "items": all_items,
                            "logo": EMBY_CONFIG['platform_logo'],
                            "adult": "no",
                            "premium": "no"
                        }
                    ]
                }
                
                with open("db.json", "w", encoding="utf-8") as f:
                    json.dump(final_db, f, indent=2, ensure_ascii=False)
                
                print(f"Success: {len(all_items)} movies saved to db.json")
        else:
            print("Login Failed")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fetch_ott_data()
    fetch_emby_movies()
