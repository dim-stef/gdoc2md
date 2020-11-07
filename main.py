from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from mdutils.mdutils import MdUtils
import re

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/documents.readonly']

# The ID of a sample document.
DOCUMENT_ID = '1XkBuOBcy4g69mRGiHzLAFff_qDwadPKogV3E-lnNcgc'


# '1L1vU0YWf1PjVMc7LL_nFTA0lApuC4hlVgjztXQ-MLSU'
# '16U5sLssOMuG8X8GF-qIo7VXW9BQJ_E0QIz6C5CzP7t0'
# '1XkBuOBcy4g69mRGiHzLAFff_qDwadPKogV3E-lnNcgc'

def is_heading(paragraph):

    if "HEADING" in paragraph.get('paragraphStyle').get('namedStyleType'):
        print("in")
        return True
    return False


def main():
    """Shows basic usage of the Docs API.
    Prints the title of a sample document.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('docs', 'v1', credentials=creds)

    # Retrieve the documents contents from the Docs service.
    document = service.documents().get(documentId=DOCUMENT_ID).execute()
    document.get('inlineObjects')
    mdFile = MdUtils(file_name='Example_Markdown', title=document.get('title'))

    for item in document['body']['content']:
        if item.get('paragraph'):
            bullet_list = []
            if item.get('paragraph').get('bullet'):
                bullet_point = ''
                for element in item.get('paragraph').get('elements'):
                    content = element.get('textRun').get('content')
                    bullet_point = bullet_point + content
                mdFile.new_line('- ' + bullet_point.rstrip('\n').strip())
                '''for element in item.get('paragraph').get('elements'):
                    content = element.get('textRun').get('content')
                    bullet_list.append(content.rstrip('\n').strip())
                    mdFile.new_list(bullet_list)'''
            else:
                for element in item.get('paragraph').get('elements'):
                    # search for images
                    if element.get('inlineObjectElement'):
                        inline_object = document.get('inlineObjects'). \
                            get(element.get('inlineObjectElement').get('inlineObjectId'))
                        object_properties = inline_object.get('inlineObjectProperties').get('embeddedObject')
                        image_path = object_properties.get('imageProperties').get('contentUri')
                        mdFile.new_line(mdFile.new_inline_image(text='image', path=image_path))

                        # add an empty character to prevent image collision with text
                        mdFile.write(' ')

                    # search for text elements
                    if element.get('textRun'):
                        content = element.get('textRun').get('content')

                        #  for now escaping all dots
                        #  TODO instead of escaping all dots, escape literals like (N.) where N is any number
                        content = re.sub(r'\.', '\.', content)

                        if content == '\n':
                            mdFile.new_line()
                            continue
                        try:
                            is_bold = element.get('textRun').get('textStyle').get('bold')
                            is_italic = element.get('textRun').get('textStyle').get('italic')
                        except AttributeError:
                            is_italic = False
                            is_bold = False
                        bold_italics_code = ''
                        if is_bold:
                            bold_italics_code = bold_italics_code + 'b'
                        if is_italic:
                            bold_italics_code = bold_italics_code + 'i'

                        # find newlines in text
                        add_new_line = False
                        if '\n' in content:
                            add_new_line = True

                        # find if text starts with space or tab
                        starts_with_space = False
                        if re.match(r'\s', content):
                            starts_with_space = True

                        # add the white space before any formatting to prevent breaking the format
                        if starts_with_space:
                            mdFile.write(' ')

                        # if these conditions meet we should transform the text to a header
                        # google docs is weird with its results so we have to check a lot of conditions
                        _is_heading = is_heading(item.get('paragraph'))
                        magnitude = element.get('textRun').get('textStyle', {}).get('fontSize', {}).get('magnitude') or \
                            element.get('textRun').get('fontSize', {}).get('magnitude')
                        if _is_heading:
                            mdFile.new_header(level=2, title=content.rstrip('\n').lstrip(), style='setext',
                                              add_table_of_contents='n')
                        # else just write plain text
                        else:
                            mdFile.write(content.rstrip('\n').lstrip(),
                                         bold_italics_code=bold_italics_code)

                        # add them after all formatting
                        if add_new_line:
                            # alternatively use mdFile.write('\n') to add a completely new line
                            # mdFile.write('\\')
                            mdFile.write('\n')
            # add a space between each element
            spacing = item.get('paragraph').get('paragraphStyle').get('lineSpacing')
            if spacing:
                mdFile.write((int(spacing) // 100) * '\n')
            else:
                pass
                #mdFile.new_line()
                # mdFile.write('\n')
    #mdFile.new_table_of_contents(table_title='Contents', depth=2)
    mdFile.create_md_file()
    print('The title of the document is: {}'.format(document.get('title')))


if __name__ == '__main__':
    main()
