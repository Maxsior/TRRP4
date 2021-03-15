import os
import requests
import click
from mimetypes import guess_type
import base64

HOST = os.getenv('SERVER_HOST') or 'http://localhost:55220'


@click.command()
@click.option('--file', '--image', '-f', required=True, prompt=True, help="Image to upload")
@click.option('--out', '-o', required=False, help="Dir to save")
def upload(file, out='.'):
    mime = guess_type(file)[0] or ''
    if not mime.startswith('image'):
        click.echo(f'File {file} is not an image')
        return

    name, _, ext = file.rpartition('.')
    name = os.path.basename(name)

    click.echo('uploading...')
    with open(file, 'rb') as file:
        r = requests.post(HOST, files={'image': file})
        faces = r.json()['faces']

    try:
        click.echo(f'Found {len(faces)} faces')
        for i, face in enumerate(faces):
            if not os.path.exists(out):
                os.mkdir(out)
            with open(os.path.join(out, f'{name}_cropped_{i}.{ext}'), 'wb') as file:
                file.write(base64.b64decode(face))
    except FileNotFoundError as e:
        print(e)
        click.echo('File does not exist or not accessible')


if __name__ == '__main__':
    upload()
