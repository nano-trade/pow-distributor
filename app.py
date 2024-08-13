import os
from flask import Flask, request, jsonify
import asyncio
import aiohttp
from aiohttp import ClientError
from collections import OrderedDict
from dotenv import load_dotenv
import nanopy
load_dotenv()

class Cache:
    def __init__(self, capacity=1000):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key):
        if key not in self.cache:
            return None
        self.cache.move_to_end(key)
        return self.cache[key]

    def set(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)

cache = Cache()
app = Flask(__name__)

# Extract URLs from environment variable
URLS = os.getenv("URLS").split(';') if os.getenv("URLS") else []

async def fetch(session, url, data):
    try:
        async with session.post(url, json=data) as response:
            if response.status == 200:
                json_response = await response.json()
                #print(f"Response from {url}: {json_response}")  # Debugging line
                if "work" in json_response and "error" not in json_response:
                    # Extract work, hash, and optionally difficulty from the response
                    work = json_response.get("work")
                    _hash = data.get("hash")  # Assuming the hash sent is what you're validating against
                    difficulty = json_response.get("difficulty", None)
                    # Validate the work using nanopy
                    if nanopy.work_validate(work, _hash, difficulty=difficulty):
                        return json_response
    except (ClientError, asyncio.TimeoutError, aiohttp.ContentTypeError) as e:
        #print(f"Error fetching from {url}: {e}")
        pass
    return None  # Return None if the work is invalid or in case of any failure

async def get_work(hash_value, difficulty=None, max_attempts=5):
    cached_result = cache.get(hash_value)
    if cached_result is not None:
        return cached_result

    data = {"action": "work_generate", "hash": hash_value}
    if difficulty is not None:
        data["difficulty"] = difficulty

    async with aiohttp.ClientSession() as session:
        for attempt in range(max_attempts):
            tasks = [fetch(session, url, data) for url in URLS]
            for future in asyncio.as_completed(tasks):
                result = await future
                if result is not None:
                    cache.set(hash_value, result)
                    return result
            print(f"Attempt {attempt + 1} failed, retrying...")

    return None

@app.route("/pow", methods=["POST"])
def pow_distributor():
    content = request.json
    hash_value = content.get("hash")
    difficulty = content.get("difficulty", None)

    if not hash_value:
        return jsonify({"error": "hash_value is required"}), 400

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(get_work(hash_value, difficulty))

    if result:
        return jsonify(result)
    else:
        return jsonify({"error": "Unable to generate work. Please try again later."}), 500

if __name__ == "__main__":
    app.run(debug=False, threaded=True, host=os.getenv("HOST"), port=int(os.getenv("PORT")))