import requests
import json
import os

EMBY_CONFIG = {
    "server": "https://play.roarzone.info",
    "username": "roarzone_guest",
    "password": "",
    "deviceId": "1e58531d-f79d-420e-8d1f-275900e30433"
}

def fetch_ott_data():
    # Mandamina ny angon-drakitra OTT
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

def fetch_emby_movies(parent_id, platform_name, save_filename, platform_logo):
    # Maka ny sarimihetsika avy amin'ny Emby
    folder_name = "wak_tu"
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    print(f"Mandamina Emby: {platform_name} (ID: {parent_id})")
    auth_url = f"{EMBY_CONFIG['server']}/emby/Users/AuthenticateByName"
    auth_header = f"MediaBrowser Client=\"Emby Web\", Device=\"GitHub Action\", DeviceId=\"{EMBY_CONFIG['deviceId']}\", Version=\"4.9.1.80\""
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
                "Fields": "PrimaryImageTag,ProductionYear",
                "api_key": token
            }
            items_res = requests.get(items_url, params=params, timeout=20, verify=False)
            items_data = items_res.json()
            if "Items" in items_data:
                all_items = []
                for item in items_data["Items"]:
                    m_id = item["Id"]
                    original_name = item["Name"]
                    year = item.get("ProductionYear")
                    if year:
                        display_title = f"{original_name} ({year})"
                    else:
                        display_title = original_name
                    all_items.append({
                        "id": original_name,
                        "title": display_title,
                        "poster": f"{EMBY_CONFIG['server']}/emby/Items/{m_id}/Images/Primary?quality=90&api_key={token}",
                        "stream_url": f"{EMBY_CONFIG['server']}/emby/Videos/{m_id}/stream?static=true&api_key={token}",
                        "headers": {"Referer": f"{EMBY_CONFIG['server']}/"}
                    })
                hero_list = all_items[:1]
                final_db = {
                    "hero": hero_list,
                    "categories": [
                        {
                            "name": platform_name,
                            "items": all_items,
                            "logo": platform_logo,
                            "adult": "no",
                            "premium": "no"
                        }
                    ]
                }
                db_path = os.path.join(folder_name, save_filename)
                with open(db_path, "w", encoding="utf-8") as f:
                    json.dump(final_db, f, indent=2, ensure_ascii=False)
                print(f"Fahombiazana: sarimihetsika {len(all_items)} voatahiry ao amin'ny {db_path}")
        else:
            print(f"Tsy nahomby ny fidirana ho an'ny {platform_name}")
    except Exception as e:
        print(f"Hadisoana ho an'ny {platform_name}: {e}")

if __name__ == "__main__":
    fetch_ott_data()
    
    # Fanavaozana ny rakitra JSON rehetra
    fetch_emby_movies("3", "Bollywood Movies", "db.json", "https://lh3.googleusercontent.com/Zf8BDyJwIg3sVzRopsN8eqkRKQPmHuPn1TdnpCpta3IKeB7Nxvjv9W3MzQEIFUD_lPw=h315")
    fetch_emby_movies("7660", "South India Movies", "db2.json", "https://cdn.aptoide.com/imgs/c/2/6/c26e21b6bf7ff848422752e80673074f_icon.png")
    fetch_emby_movies("9031", "Hollywood Movies", "db3.json", "https://play-lh.googleusercontent.com/xq5SE_5ZLt6pafKq2s9anWIvwj7VC4UJnur6gn66W_CwuKyeC6ru9z-XO-YqUOjTUHkklKzRGn_C_fA0w6viFA")
    fetch_emby_movies("137971", "Kolkata Movies", "db4.json", "https://yt3.googleusercontent.com/VSSbeS5NgUikFBxR3xMwhVzsLr70D1I361KjhpBIgCY9ktbmZajOryDiISlNFOcSpDLDUzioJg=s900-c-k-c0x00ffffff-no-rj")
    fetch_emby_movies("137931", "Bangla Movies", "db5.json", "https://static4.tgstat.ru/channels/_0/16/16f74c51d97408ae467e7c0b8b2423d9.jpg")
