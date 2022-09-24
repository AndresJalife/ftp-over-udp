import click

@click.command()
@click.option('-v', '--verbose', default=1, help='increase output verbosity')
@click.option('-q', '--quiet', default=1, help='decrease output verbosity')
@click.option('-H', '--host', default=1, help='service IP address')
@click.option('-p', '--port', default=1, help='service port')
@click.option('-d', '--dst', default=".", help='dst destination file path')
@click.option('-n', '--name', default=1, help='file name')

def main(verbose, quiet, host, port, dst, name):
    """Comando para descargar un archivo mediante custom-ftp"""
    click.echo(f"Hello {name}!")

if __name__ == '__main__':
    main()
