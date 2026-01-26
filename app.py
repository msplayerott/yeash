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
                p_name = platform.get("name")
                p_logo = platform.get("logo")
                p_adult = platform.get("adult", "no")
                p_premium = platform.get("premium", "no")
                json_url = platform.get("json_url")
                
  
                file_save_name = p_name.replace(" ", "_")
                
                print(f"Processing {p_name}...")
                
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
                    print(f"Success: {filename}")
                    
                except Exception as e:
                    print(f"Error processing content for {p_name}: {e}")
                    
    except Exception as e:
        print(f"Error fetching main config: {e}")

if __name__ == "__main__":
    fetch_and_save_data()
