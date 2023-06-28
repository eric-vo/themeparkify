import openapi_client
from openapi_client.api import destinations_api

configuration = openapi_client.Configuration()


def search_for_park(park_name, destination_name=None):
    """Search for a park containing the given query/queries.

    Returns a list of matching parks
    or an error message if something goes wrong.
    """

    # Enter a context with an instance of the API client
    with openapi_client.ApiClient(configuration) as api_client:
        # Create an instance of the API class
        api_instance = destinations_api.DestinationsApi(api_client)

        try:
            # Get list of destinations from the ThemeParks API
            destinations = api_instance.get_destinations()["destinations"]
        except openapi_client.ApiException as e:
            return (
                "Exception when calling DestinationsApi->get_destinations: "
                + e
            )

    destinations_to_search = []

    # If the user specified a destination query,
    # search for matching destinations and search through those
    # Otherwise, search through all destinations
    if destination_name is not None:
        for destination in destinations:
            if destination_name in destination["name"]:
                destinations_to_search.append(destination)
    else:
        destinations_to_search = destinations

    matches = []

    for destination in destinations_to_search:
        for park in destination["parks"]:
            if park_name in park["name"]:
                matches.append({
                    "destination": destination["name"],
                    "name": park["name"],
                    "id": park["id"]
                })

    return matches
