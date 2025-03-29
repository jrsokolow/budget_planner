import click
from uploader import upload_file_to_s3

@click.command()
@click.argument('file_name', type=click.Path(exists=True))
@click.option('--bucket', required=True, help='Nazwa bucketu S3, np. "moj-bucket"')
@click.option('--object-name', default=None, help='Ścieżka w S3 (opcjonalnie)')
def main(file_name, bucket, object_name):
    """Wysyła plik do S3.

    FILE_NAME – lokalna ścieżka do pliku
    """
    upload_file_to_s3(file_name, bucket, object_name)

if __name__ == '__main__':
    main()
