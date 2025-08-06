import click 

# @click.command()
# def hello():
#     click.echo('hello ji'*5)



@click.command()
@click.option('--count', default=1, help='number of greetings')
@click.argument('name')
def hello(count, name):
    for x in range(count):
        click.echo(f"Hello {name}!")


if __name__ == '__main__':
    hello()

############################################## Step 1: CLI Application Implementation ######################## 
@click.command()
@click.argument('Query', help='Enter you query or what you want to build')
def generate(Query):
    click.echo('Query')