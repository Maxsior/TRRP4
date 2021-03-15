import multiprocessing
import click
import os


@click.command()
@click.option('--file', '--image', '-f', required=True, prompt=True, help="Image to upload")
@click.option('-n', type=int)
def upload(file, n):
    with multiprocessing.Pool() as pool:
        client = os.path.join(os.path.dirname(__file__), 'main.py')
        pool.map(os.system, [f'python3 {client} -o {x} -f {file}' for x in range(n)])


if __name__ == '__main__':
    upload()
