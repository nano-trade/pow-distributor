# Nano PoW Distributor

This project is a Flask-based web service that distributes Proof of Work (PoW) generation requests across multiple RPC endpoints for the Nano and Banano networks. The service sends requests to all specified RPCs simultaneously and quickly returns the first valid response it receives, ensuring that the fastest available result is used. The service can be customized to use different RPC URLs and provides a simple HTTP API for submitting PoW requests.

## Features

- **Asynchronous Requests:** Utilizes `aiohttp` for non-blocking, asynchronous HTTP requests to multiple RPC servers.
- **Caching:** Implements an in-memory LRU (Least Recently Used) cache to store and reuse valid PoW results.
- **Validation:** Integrates with `nanopy` to validate the work results received from the RPC servers.
- **Retry Mechanism:** Automatically retries requests to RPC endpoints a configurable number of times if the initial attempts fail.
- **Support for Nano and Banano:** This service can be used with both Nano and its forks, such as, the Banano network.

## How It Works

1. **Environment Setup:** The service reads the list of RPC URLs from an environment variable (`URLS`). These URLs should be separated by semicolons (`;`).
2. **Handling Requests:** When a request is received at the `/pow` endpoint, the service:
   - Parses the `hash` and `difficulty` (optional) from the request body.
   - Checks if a valid PoW result for the provided `hash` is already cached.
   - If not cached, it sends asynchronous requests to all specified RPC URLs **simultaneously**.
   - The service returns the **first valid response** it receives from any of the RPCs, ensuring that the fastest valid result is used.
   - Validates the received work using `nanopy`.
   - Caches the result if valid and returns it to the client.
3. **Retries:** If no valid work is obtained in the first attempt, the service retries up to a specified number of times (`max_attempts`).

## Installation and Setup

### Prerequisites

- Python 3.7 or higher
- `pip` for Python package management
- `virtualenv` (optional but recommended)

### Steps to Set Up and Run the Service

1. **Clone the Repository**

   ```bash
   git clone <repository_url>
   cd <repository_directory>
   ```

2. **Create a Virtual Environment**

   (Optional, but recommended to avoid dependency conflicts)

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**

   Create a `.env` file in the project root or modify the `.env.example` provided. Replace the example RPC URLs with your own:

   ```plaintext
   HOST="127.0.0.1"
   PORT=8080
   URLS=https://your.nano.rpc;https://your.banano.rpc;https://another.rpc/proxy
   ```

   - `HOST`: IP address where the service will run.
   - `PORT`: Port number for the service.
   - `URLS`: A semicolon-separated list of RPC URLs to be used for PoW generation.

5. **Run the Service**

   Start the Flask application:

   ```bash
   python app.py
   ```

   Alternatively, you can run the service in the background using `nohup`:

   ```bash
   nohup python3 app.py </dev/null >/dev/null 2>&1 &
   ```

   Or simply use this (generates a nohup.out file for logs):

   ```bash
   nohup python3 app.py &
   ```

6. **Access the API**

   The service will be accessible at `http://<HOST>:<PORT>/pow`. You can send a POST request to this endpoint with the following JSON body:

   ```json
   {
     "hash": "<hash_value>",
     "difficulty": "<optional_difficulty>"
   }
   ```

   The service will respond with either a valid PoW result or an error message if the work could not be generated.

## Example Use Cases

- **Nano/Banano Wallets:** Integrate this service into wallets to offload PoW generation to external servers.
- **Distributed Systems:** Use the service to distribute PoW generation across multiple endpoints for load balancing.

## Notes

- **Free RPCs:** You can use free RPCs from this list: [Public Nano Nodes](https://publicnodes.somenano.com/). However, it is advised to use a more reliable and dedicated solution for production environments. You can refer to this guide for better solutions: [Nano Work Generation Guide](https://docs.nano.org/integration-guides/work-generation/).
- **RPC Reliability:** Ensure the RPC URLs you use are trusted and reliable.
- **Custom Configuration:** Adjust the cache size and retry attempts as needed based on your specific use case.
- **Service Flexibility:** The service is designed to be flexible and can be customized for different environments and needs.

## Contributing

Feel free to submit issues or pull requests for any improvements or bug fixes.

## License

This project is licensed under the MIT License.