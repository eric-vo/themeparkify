import openapi_client
from openapi_client.api import destinations_api
from openapi_client.api import entities_api

configuration = openapi_client.Configuration()


# ThemeParks API: https://api.themeparks.wiki/docs/v1/
def get_destinations():
    """Get destinations via an API call."""

    with openapi_client.ApiClient(configuration) as api_client:
        # Create an instance of the API class
        api_instance = destinations_api.DestinationsApi(api_client)

        # Get list of destinations from the ThemeParks API
        try:
            return api_instance.get_destinations()["destinations"]
        except openapi_client.ApiException as e:
            log_error("DestinationsApi->get_destinations", e)


def get_entity(entity_id, type=None, year=None, month=None):
    """Get entity via an API call."""

    with openapi_client.ApiClient(configuration) as api_client:
        # Create an instance of the API class
        api_instance = entities_api.EntitiesApi(api_client)

        if type is not None:
            match type:
                case "children":
                    try:
                        return api_instance.get_entity_children(entity_id)
                    except openapi_client.ApiException as e:
                        log_error("EntitiesApi->get_entity_children", e)
                case "live":
                    try:
                        return api_instance.get_entity_live_data(entity_id)
                    except openapi_client.ApiException as e:
                        log_error("EntitiesApi->get_entity_live_data", e)
                case "schedule_upcoming":
                    try:
                        return api_instance.get_entity_schedule_upcoming(
                            entity_id
                        )
                    except openapi_client.ApiException as e:
                        log_error(
                            "EntitiesApi->get_entity_schedule_upcoming", e
                        )
                case "schedule_year_month":
                    try:
                        return api_instance.get_entity_schedule_year_month(
                            entity_id, year, month
                        )
                    except openapi_client.ApiException as e:
                        log_error(
                            "EntitiesApi->get_entity_schedule_year_month", e
                        )
        else:
            try:
                return api_instance.get_entity(entity_id)
            except openapi_client.ApiException as e:
                log_error("EntitiesApi->get_entity", e)


def log_error(call, e):
    """Print an error to the console.

    Returns the generated error message.
    """

    print(f"Exception when calling {call}: {e}")


# park_query is required to improve searching times
def search_for_entities(
    entity_query,
    destination_ids,
    park_query,
    destination_query=None,
    entity_type=None
):
    """Search for entities with the given queries and destination IDs.

    Returns a list of matching entities.
    """

    if destination_query is not None:
        parks = search_for_parks(
            park_query, destination_ids, destination_query
        )
    else:
        parks = search_for_parks(park_query, destination_ids)

    entity_query = entity_query.strip().lower()

    if entity_type is not None:
        entity_type = entity_type.strip().upper()

    matches = []

    for park in parks:
        park = get_entity(park["id"], "children")

        for child in park["children"]:
            if (
                entity_type is not None
                and entity_type != str(child["entity_type"])
            ):
                continue

            if entity_query in child["name"].lower():
                matches.append(child)

    return matches


def search_for_destinations(destination_query, destination_ids=None):
    """Search for a destination with the given queries and destination IDs.

    Returns a list of matching destinations.
    """

    destinations = get_destinations()

    if destination_ids is not None:
        destinations_to_search = []

        for destination in destinations:
            if destination["id"] in destination_ids:
                destinations_to_search.append(destination)
    else:
        destinations_to_search = destinations

    destination_query = destination_query.strip().lower()

    matches = []

    for destination in destinations_to_search:
        if destination_query in destination["name"].lower():
            matches.append(destination)

    return matches


def search_for_parks(
    park_query, destination_ids, destination_query=None
):
    """Search for a park with the given queries and destination IDs.

    Returns a list of matching parks.
    """

    if destination_query is not None:
        destinations = search_for_destinations(
            destination_query, destination_ids
        )
    else:
        destinations = search_for_destinations("", destination_ids)

    park_query = park_query.strip().lower()

    matches = []

    for destination in destinations:
        for park in destination["parks"]:
            if park_query in park["name"].lower():
                park["destination_name"] = destination["name"]
                matches.append(park)

    return matches
