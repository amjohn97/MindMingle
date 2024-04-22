"""Module to handle user input and call the necessary functions."""

from .utils import get_top_institutions_and_professors


def scholarquest():
    """Below is function to handle user input and call the functions."""
    topic = input("Enter the topic of interest: ")
    country = input("Enter the country (optional) Press enter for skip: ")
    if country.strip() == "":
        country = None
    get_top_institutions_and_professors(topic, country)


if __name__ == "__main__":
    scholarquest()
