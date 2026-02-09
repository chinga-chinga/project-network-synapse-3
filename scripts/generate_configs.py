"""Query Infrahub and render Jinja2 templates to generate device configurations."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader


TEMPLATE_DIR = Path(__file__).parent.parent / "templates"


def get_jinja_env() -> Environment:
    return Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))


def generate_bgp_config(device_data: dict) -> str:
    env = get_jinja_env()
    template = env.get_template("arista_bgp.j2")
    return template.render(**device_data)


def generate_interface_config(device_data: dict) -> str:
    env = get_jinja_env()
    template = env.get_template("arista_interfaces.j2")
    return template.render(**device_data)


if __name__ == "__main__":
    pass
