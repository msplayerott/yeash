import requests
import json
import os

def fetch_and_save_data():
    main_url = "https://allinonedev.top/main.json"
    folder_name = "wak_tu"
    

    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"Created folder: {folder_name}")

    try:
        response = requests.get(main_url)
        main_data = response.json()
        
        if "ott_platforms" in main_data:
            for platform in main_data["ott_platforms"]:
              
                name = platform["name"].replace(" ", "_")
                json_url = platform["json_url"]
                
                print(f"Fetching data for {name}...")
                
                try:
                    p_response = requests.get(json_url)
                    p_data = p_response.json()
                    filename = os.path.join(folder_name, f"{name}.json")
                    with open(filename, "w", encoding="utf-8") as f:
                        json.dump(p_data, f, indent=2, ensure_ascii=False)
                    print(f"Successfully saved to {filename}")
                    
                except Exception as e:
                    print(f"Failed to fetch {name}: {e}")
                    
    except Exception as e:
        print(f"Error fetching main JSON: {e}")

if __name__ == "__main__":
    fetch_and_save_data()
