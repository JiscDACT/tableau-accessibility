from lxml.etree import XMLParser, parse
import os
import sys
from yaml import load, loader

# We need to use the 'huge' parser as these docs are really big
p = XMLParser(huge_tree=True)


def get_parent_zone(item):
    while item is not None:
        if item.tag == 'zone':
            return item
        item = item.getparent()


def get_button(tree, dashboard_name, caption):
    button = tree.xpath(".//dashboard[@name='"+dashboard_name+"']//caption[text()='" + caption + "']")
    if button is not None and button.__len__() > 0:
        zone = get_parent_zone(button[0])
        return zone
    return None


def get_parameter(tree, dashboard_name, parameter):
    param = '[Parameters].['+parameter+']'
    parameter = tree.xpath(".//dashboard[@name='"+dashboard_name+"']//zone[@param='" + param + "']")
    if parameter is not None and parameter.__len__() > 0:
        zone = parameter[0]
        return zone
    return None


def get_filter(tree, dashboard_name, filter):
    filter = ':'+filter+':'
    parameter = tree.xpath(".//dashboard[@name='"+dashboard_name+"']//zone[contains(@param, '" + filter + "')]")
    if parameter is not None and parameter.__len__() > 0:
        zone = parameter[0]
        return zone
    return None


def fix_tabs(input_filename, output_filename, configuration):
    with open(input_filename, 'r', encoding='utf-8') as f:  # open in readonly mode
        tree = parse(f, parser=p)

        zone_id = 0
        for dashboard_name in configuration:
            tab_order = configuration[dashboard_name]
            zone_id += 100

            # Start providing IDs for the named items
            for item in tab_order:
                zone = tree.xpath("//dashboard[@name='"+dashboard_name+"']//zone[@name='"+item+"']")
                if zone is not None and zone.__len__() > 0:
                    zone = zone[0]
                if zone is None or zone.__len__() == 0:
                    zone = get_button(tree, dashboard_name, item)
                if zone is None or zone.__len__() == 0:
                    zone = get_parameter(tree, dashboard_name, item)
                if zone is None or zone.__len__() == 0:
                    zone = get_filter(tree, dashboard_name, item)
                zone.set("id", zone_id.__str__())
                zone.set("is-modified", '1')
                zone_id += 1

            # Add IDs to everything else in document order
            zones = tree.xpath('//dashboard[@name="' + dashboard_name + '"]//zone')
            for zone in zones:
                if not zone.get("is-modified"):
                    zone.set("id", zone_id.__str__())
                    zone_id += 1

            dashboard = tree.find("//dashboard[@name='"+dashboard_name+"']")

            # Duplicate IDs in device layouts cause problems so get rid of them...
            layouts = dashboard.find("devicelayouts")
            if layouts is not None:
                dashboard.remove(layouts)

    tree.write(output_filename, encoding='utf-8')


if __name__ == "__main__":

    # Defaults
    input_path = 'testing.twb'
    output_path = 'output.twb'
    manifest_path = 'manifest.txt'

    if sys.argv.__len__() > 1:
        input_path = sys.argv[1]
        if not os.path.exists(input_path):
            print('Input workbook does not exist')
            exit()
        else:
            print("Input workbook: "+input_path)
    if sys.argv.__len__() > 2:
        output_path = sys.argv[2]
        print("Output workbook: "+output_path)

    if sys.argv.__len__() > 3:
        manifest_path = sys.argv[3]
        if not os.path.exists(input_path):
            print('Manifest does not exist')
            exit()
        else:
            print("Manifest: "+manifest_path)

    # Load the configuration/manifest
    with open(manifest_path, 'r') as file:
        configuration = load(file, Loader=loader.SafeLoader)

    fix_tabs(input_path, output_path, configuration)
