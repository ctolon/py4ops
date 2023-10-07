import click


def list_or_str(ctx, param, value):
    if value is None:
        return None
    elif isinstance(value, list):
        return value
    elif isinstance(value, str):
        return value.split()
        #return [value]
    else:
        raise click.BadParameter('parameter must be a string or a list of strings')
