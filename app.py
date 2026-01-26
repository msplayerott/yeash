import requests
import json
import os

def fetch_and_save_data():
    main_url = "https://allinonedev.top/main1.json"
    folder_name = "wak_tu"
    
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    try:
        response = requests.get(main_url)
        main_data = response.json()
        
        if "ott_platforms" in main_data:
            for platform in main_data["ott_platforms"]:
                name = platform.get("name", "Unknown").replace(" ", "_")
                json_url = platform.get("json_url")
                
                
                platform_meta = {
                    "name": platform.get("name"),
                    "logo": platform.get("logo"),
                    "adult": platform.get("adult", "no"),
                    "premium": platform.get("premium", "no")
                }
                
                print(f"Fetching data for {name}...")
                
                try:
                    p_response = requests.get(json_url)
                    p_data = p_response.json()
                    
                    
                    final_output = {
                        "platform_info": platform_meta,
                        "content": p_data
                    }
                    
                    filename = os.path.join(folder_name, f"{name}.json")
                    with open(filename, "w", encoding="utf-8") as f:
                        json.dump(final_output, f, indent=2, ensure_ascii=False)
                    print(f"Successfully saved {filename} with metadata.")
                    
                except Exception as e:
                    print(f"Failed to fetch content for {name}: {e}")
                    
    except Exception as e:
        print(f"Error fetching main JSON: {e}")

if __name__ == "__main__":
    fetch_and_save_data()
