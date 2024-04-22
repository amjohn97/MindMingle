"""Utility functions for ScholarQuest package."""

import requests
import urllib.parse


def get_publications_by_topic(topic, country=None):
    """Query to retrieve publication data based on given topic.

    Parameters are topic (str): The topic of interest.
    country (str): (Optional) The country filter for publications.
    Returns a list of dicts: A list of publication data as dictionary.
    """
    # Replace spaces with '+' symbol
    topic = urllib.parse.quote_plus(topic)

    # Construct the API URL
    url = (
        f"https://api.openalex.org/works?page=1&"
        f"filter=default.search:{topic}"
    )

    # Add country filter to the URL if provided
    if country:
        country = urllib.parse.quote_plus(country)
        url = (
            f"https://api.openalex.org/works?page=1&"
            f"filter=default.search:{topic},"
            f"authorships.countries:countries/{country}"
        )
    # Make the API request
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        publications = response.json().get("results", [])
        # Extract relevant information from each publication
        extracted_data = []
        for pub in publications:
            # Extracting author names from authorships
            authors = []
            author_ids = []
            institution_data_list = []
            current_institution_data_list = []
            author_h_indices = []
            for authorship in pub.get("authorships", []):
                author_name = authorship["author"]["display_name"]
                author_id = authorship["author"]["id"]
                author_h_index, institutiono = get_author_h_index(author_id)
                authors.append(author_name)
                author_h_indices.append(author_h_index)
                author_ids.append(author_id)

                # Extract institution details
                if institutiono:
                    current_institution_data_list.append(
                        {
                            "name": institutiono,
                        }
                    )

                # Extract institution details
                institutions = authorship.get("institutions", [])
                for inst in institutions:
                    institution_id = inst.get("id")
                    institution_details = get_institution_details(
                        institution_id
                    )
                    if institution_details:
                        institution_loc = {
                            "name": institution_details.get("display_name"),
                            "latitude": institution_details.get("geo", {}).get(
                                "latitude"
                            ),
                            "longitude": institution_details.get(
                                "geo", {}
                            ).get("longitude"),
                            "country": institution_details.get("geo", {}).get(
                                "country"
                            ),
                            "city": institution_details.get("geo", {}).get(
                                "city"
                            ),
                        }
                        institution_data_list.append(institution_loc)

            pub_data = {
                "title": pub.get("display_name", "Title not available"),
                "institutions": institution_data_list,
                "current_institution": current_institution_data_list,
                "authors": authors,
                "author_ids": author_ids,
                "cited_by_count": pub.get("cited_by_count", 0),
                "author_h_indices": author_h_indices,
            }
            extracted_data.append(pub_data)

        return extracted_data
    else:
        print(
            f"Failed to retrieve publication data."
            f"Status code: {response.status_code}"
        )
        return []


def get_author_h_index(author_id):
    """Fetch the h-index of an author from their OpenAlex ID.

    Parameters: author_id (str): The OpenAlex ID of the author.

    Returns: int: The h-index of the author.
    str: The institution of the author.
    """
    # Make the API request
    author_number = author_id.split("/")[-1]
    author_url = f"https://api.openalex.org/people/{author_number}"
    author_response = requests.get(author_url)

    # Check if the request was successful
    if author_response.status_code == 200:
        author_data = author_response.json().get("summary_stats", {})
        h_index = author_data.get("h_index", 0)
        affiliations = author_response.json().get("affiliations", [])
        if affiliations:
            institution = affiliations[0]["institution"].get(
                "display_name", "Unknown"
            )
        else:
            institution = "Unknown"
        return h_index, institution
    else:
        return 0, "Unknown"


def get_institution_details(institution_id):
    """Fetch details of an institution from its OpenAlex ID.

    Parameters:institution_id (str): The OpenAlex ID of the institution.

    Returns:dict: A dictionary containing details of the institution.
    """
    # Construct the API URL
    url = f"https://api.openalex.org/institutions/{institution_id}"

    # Make the API request
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        institution_data = response.json()
        return institution_data
    else:
        return None


def calculate_institution_scores(publications):
    """Calculate scores for institutions based on following.

    publication count, citation count, and author h-indices.
    Parameters: publications: List of publication data, as a dictionary.

    Returns: dict: A dictionary with keys: institution names, values: scores.
    """
    institution_scores = {}

    for pub in publications:
        institutions = pub.get("institutions", [])
        cited_by_count = pub.get("cited_by_count", 0)
        author_h_indices = pub.get("author_h_indices", [])

        for inst in institutions:
            institution_name = inst.get("name")
            publication_count = 1  # Each publication adds 1 to the count

            # Calculate the institution score
            score = (
                (publication_count * 0.4)
                + (cited_by_count * 0.4)
                + (sum(author_h_indices) * 0.2)
            )

            # Update or initialize the score for the institution
            if institution_name in institution_scores:
                institution_scores[institution_name] += score
            else:
                institution_scores[institution_name] = score

    return institution_scores


def calculate_author_scores(publications):
    """Calculate scores for authors on contributions to given topic.

    Parameters: publications: A list of publication data as dictionary.

    Returns: dict: keys are author names and values are corresponding scores.
    """
    author_scores = {}

    for pub in publications:
        authors = pub.get("authors", [])
        cited_by_count = pub.get("cited_by_count", 0)
        author_h_indices = pub.get("author_h_indices", [])

        for author_name, h_index in zip(authors, author_h_indices):
            # Calculate the author score based on h-index
            score = 5 * h_index + cited_by_count

            # Update or initialize the score for the author
            if author_name in author_scores:
                author_scores[author_name] += score
            else:
                author_scores[author_name] = score

    return author_scores


def get_top_professors(publications, top_n=5, top_universities=30):
    """Identify the top professors in the field based on their contributions.

    Parameters: publications: List of publication data.
    top_n (int): Number of top professors to retrieve.
    top_universities (int): Number of top universities to consider.

    Returns: list of tuples: List of tuples(professor_name, author_id).
    """
    author_scores = calculate_author_scores(publications)

    # Sort the author scores dictionary based on scores in descending order
    sorted_scores = sorted(
        author_scores.items(), key=lambda x: x[1], reverse=True
    )

    # Extract the top professors and their author IDs
    top_professors = []

    for author, _ in sorted_scores:
        # Limit the number of professors to retrieve
        if len(top_professors) >= top_n:
            break

        # Find the author's ID from the publications data
        author_info = None
        for pub in publications:
            if author in pub["authors"]:
                author_index = pub["authors"].index(author)
                author_id = pub["author_ids"][author_index]
                h_index = pub["author_h_indices"][author_index]
                current_university = pub["current_institution"][author_index][
                    "name"
                ]
                author_info = (author, author_id, h_index, current_university)
                break
        # Add the author info to the list
        if author_info:
            top_professors.append(author_info)

    return top_professors


def get_top_institutions_and_professors(
    topic, country=None, top_institutions=10, top_professors=5
):
    """Get the top institutions and professors for a given topic.

    Parameters: topic (str): The topic of interest.
    country (str): (Optional) The country filter for publications.
    top_institutions (int): Number of top institutions to retrieve.
    top_professors (int): Number of top professors to retrieve.

    Returns: A tuple (top institutions, top professors).
    """
    publications = get_publications_by_topic(topic, country)
    institution_scores = calculate_institution_scores(publications)

    # Sort the institution scores dictionary in descending order
    sorted_institution_scores = sorted(
        institution_scores.items(), key=lambda x: x[1], reverse=True
    )

    # Extract the top institutions and their scores
    top_institutions_dict = dict(sorted_institution_scores[:top_institutions])

    # Print the top institutions
    print("\nTop Institutions:")
    for institution, score in top_institutions_dict.items():
        print(f"{institution}: {score:.3f}")

    top_professors = get_top_professors(
        publications, top_n=10, top_universities=3
    )

    # Print the top professors and their details
    print("\nTop Professors:")
    for professor, author_id, h_index, current_university in top_professors:
        print(
            f"{professor}: Author ID - {author_id}, "
            f"h-index - {h_index}, Current University - {current_university}"
        )

    return top_institutions_dict, top_professors
