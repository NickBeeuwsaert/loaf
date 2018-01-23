class Auth:
    def __init__(self, client):
        self.client = client
    
    def test(self):
        return self.client.api_call('GET', 'auth.test')