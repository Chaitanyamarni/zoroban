from flask import Flask, request, jsonify
import requests
from rich.console import Console
from rich.progress import Progress

app = Flask(__name__)
console = Console()

def check_player_info(target_id):
    with Progress() as progress:
        task = progress.add_task("[cyan]Fetching player data...", total=100)

        cookies = {
            'region': 'MA',
            'language': 'ar',
            'session_key': 'efwfzwesi9ui8drux4pmqix4cosane0y',
        }

        headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9,en;q=0.8",
        "Content-Type": "application/json",
        "Origin": "https://shop2game.com",
        "Referer": "https://shop2game.com/app",
        "sec-ch-ua": '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Windows",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
        "x-datadome-clientid": "10BIK2pOeN3Cw42~iX48rEAd2OmRt6MZDJQsEeK5uMirIKyTLO2bV5Ku6~7pJl_3QOmDkJoSzDcAdCAC8J5WRG_fpqrU7crOEq0~_5oqbgJIuVFWkbuUPD~lUpzSweEa",
    }

        json_data = {
            'app_id': 100067,
            'login_id': target_id,
            'app_server_id': 0,
        }

        try:
            progress.update(task, advance=30)
            res = requests.post(
                'https://shop2game.com/api/auth/player_id_login',
                cookies=cookies, headers=headers, json=json_data
            )

            if res.status_code != 200 or not res.json().get('nickname'):
                return {"error": "ID NOT FOUND"}

            player_data = res.json()
            player_name = player_data.get('nickname', 'N/A')
            region = player_data.get('region', 'N/A')

            progress.update(task, advance=35)

            ban_url = f'https://ff.garena.com/api/antihack/check_banned?lang=en&uid={target_id}'
            ban_response = requests.get(ban_url, headers={
                'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'referer': 'https://ff.garena.com/en/support/',
                'x-requested-with': 'B6FksShzIgjfrYImLpTsadjS86sddhFH',
            })

            progress.update(task, advance=35)
            ban_data = ban_response.json()

            if ban_data["status"] == "success" and "data" in ban_data:
                is_banned = ban_data["data"].get("is_banned", 0)
                period = ban_data["data"].get("period", 0)

                if is_banned:
                    ban_message = f"Banned for {period} months" if period > 0 else "Banned indefinitely"
                else:
                    ban_message = "Not banned"
            else:
                return {"error": "Failed to retrieve ban status"}

            return {
                "player_id": target_id,
                "player_name": player_name,
                "region": region,
                "status": ban_message,
                "period": f"{period} months" if is_banned and period > 0 else None
            }

        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

@app.route('/karna/ban-info', methods=['GET'])
def get_region_info():
    uid = request.args.get('uid')
    if not uid:
        return jsonify({"error": "UID parameter is required"}), 400

    result = check_player_info(uid)
    if "error" in result:
        return jsonify(result), 404

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
