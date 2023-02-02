""""
Author: Tommi Summanen
"""

import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/documents.readonly",
    "https://www.googleapis.com/auth/drive.metadata.readonly",
]

from config import GOOGLE_DRIVE_ID


# Functions taken from: https://developers.google.com/docs/api/samples/extract-text
def read_paragraph_element(element):
    """Returns the text in the given ParagraphElement.

    Args:
        element: a ParagraphElement from a Google Doc.
    """
    text_run = element.get("textRun")
    if not text_run:
        return ""
    return text_run.get("content")


def read_strucutural_elements(elements):
    """Recurses through a list of Structural Elements to read a document's text where text may be
    in nested elements.

    Args:
        elements: a list of Structural Elements.
    """
    text = ""
    for value in elements:
        if "paragraph" in value:
            elements = value.get("paragraph").get("elements")
            for elem in elements:
                text += read_paragraph_element(elem)
        elif "table" in value:
            # The text in table cells are in nested Structural Elements and tables may be
            # nested.
            table = value.get("table")
            for row in table.get("tableRows"):
                cells = row.get("tableCells")
                for cell in cells:
                    text += read_strucutural_elements(cell.get("content"))
        elif "tableOfContents" in value:
            # The text in the TOC is also in a Structural Element.
            toc = value.get("tableOfContents")
            text += read_strucutural_elements(toc.get("content"))
    return text


def read_manuscript():
    """Reads text content from all documents in a given drive, gathers them in one
    string and returns this string.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    # Get list of all documents in given folder.
    drive_service = build("drive", "v3", credentials=creds)
    documents = (
        drive_service.files()
        .list(q=f"'{GOOGLE_DRIVE_ID}' in parents", orderBy="name", fields="files(id)")
        .execute()
    )
    document_ids = [item["id"] for item in documents.get("files", [])]

    # Retrieve contents from each document.
    docs_service = build("docs", "v1", credentials=creds)
    contents = ""
    for document_id in document_ids:
        document = docs_service.documents().get(documentId=document_id).execute()
        content = document.get("body").get("content")
        contents += read_strucutural_elements(content)

    return contents


if __name__ == "__main__":
    print(read_manuscript())
