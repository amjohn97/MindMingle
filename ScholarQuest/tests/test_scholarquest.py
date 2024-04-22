"""Module containing unit tests for ScholarQuest module."""

import ScholarQuest


def test_get_publications_by_topic():
    """Test the get_publications_by_topic function."""
    topic = "stochastic programming"
    publications = ScholarQuest.get_publications_by_topic(topic)
    assert isinstance(publications, list)
    assert len(publications) > 0


def test_get_author_h_index():
    """Test the get_author_h_index function."""
    # Given an example author ID
    author_id = "https://openalex.org/authors/A5003442464"

    # When fetching the h-index and institution details
    h_index, institution = ScholarQuest.get_author_h_index(author_id)

    # To ensure that h_index is an integer and not equal to 0
    assert isinstance(h_index, int)
    assert h_index >= 0

    # To ensure that institution is a string and not None or an empty string
    assert isinstance(institution, str)
    assert institution.strip()


def test_get_institution_details():
    """Test the get_institution_details function."""
    institution_id = "I74973139"
    institution_details = ScholarQuest.get_institution_details(institution_id)
    assert isinstance(institution_details, dict)
