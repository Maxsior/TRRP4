import os
import requests
import click
from mimetypes import guess_type

HOST = os.getenv('SERVER_HOST') or 'http://localhost:5000'


@click.command()
@click.option('--file', '--image', '-f', required=True, prompt=True, help="Image to upload")
def upload(file):
    mime = guess_type(file)[0] or ''
    if not mime.startswith('image'):
        click.echo(f'File {file} is not an image')
        return

    try:
        with open(file, 'rb') as file:
            click.echo('uploading...')
            r = requests.post(HOST, files={'image': file})
            print(r)  # TODO что возвращается?
    except FileNotFoundError as e:
        print(e)
        click.echo('File does not exist or not accessible')


if __name__ == '__main__':
    upload()
