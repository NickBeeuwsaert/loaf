# Loaf
Loaf is a slack client written in python

## Why?
Why not

## Getting started

1. Create a slack app for your personal use here: https://api.slack.com/apps?new_app=1
2. Add the redirect URL 'http://127.0.0.1:6543/' to your apps permissions page
3. Put your client secret and client id in a file named `config.json`:

    ```
    {
        "client": {
            "id": "CLIENT_ID",
            "secret": "CLIENT_SECRET"
        }
    }
    ```
4. Run this to save a access token to your `config.json`

    ```
    $ python3 -m venv venv
    $ venv/bin/pip install -e.
    $ venv/bin/python -m loaf.auth
    ```

5. Run the client

    ```
    $ venv/bin/loaf
    ```
