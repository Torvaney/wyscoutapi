# wyscoutapi

wyscoutapi is an extremely basic API client for the [Wyscout API](https://apidocs.wyscout.com/) (v2 & v3).

## Usage

Install with `pip install wyscoutapi`.

To connect to the Wyscout v3 api:

```python
import wyscoutapi

client = wyscoutapi.WyscoutAPI(
    username='myusername',
    password='mypassword',
)

client.player(329061)
```

To use the v2 legacy API, or alter the rate-limit 
(defaults to [12 requests per second](https://apidocs.wyscout.com/#section/Authentication/Rate-limits)):

```python
import wyscoutapi

client = wyscoutapi.WyscoutAPI(
    username='myusername',
    password='mypassword',
    version='v2',
    requests_per_second=10
)

client.player(329061)
```

## API mocking

It can be useful to mock the API client for testing and local development.

To do this, create a custom "loader" to handle requests, and pass it to the `APIClient` constructor. 

```python
import wyscoutapi


class StubLoader:
    def __init__(self):
        pass

    def get_route_json(self, *route, **params):
        return {
            'stub': 'This is a stub response'
        }
    

client = wyscoutapi.APIClient(loader=StubLoader())
client.player(329061)
```

## Other options

Wyscout provides an OpenAPI specification for their v3 API (see [https://apidocs.wyscout.com/](https://apidocs.wyscout.com/)). 
You may prefer to create a more sophisticated API Client using code-generation tools such as [openapi-generator](https://github.com/OpenAPITools/openapi-generator) or [
openapi-python-client](https://pythonrepo.com/repo/triaxtec-openapi-python-client-python-fastapi-utilities), although as of 2021-10-01, 
I had some issues getting this to work with both of the generators linked above.