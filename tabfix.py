from lxml.etree import XMLParser, parse
import argparse
import os
import sys
from yaml import load, loader

# We need to use the 'huge' parser as these docs are really big
p = XMLParser(huge_tree=True)


def get_parent_tag(item, tag):
    while item is not None:
        if item.tag == tag:
            return item
        item = item.getparent()

def get_parent_worksheet(item):
    return get_parent_tag(item, 'worksheet')

def get_parent_dashboard(item):
    return get_parent_tag(item, 'dashboard').get("name")

def get_parent_zone(item):
    return get_parent_tag(item, 'zone')


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


def check_accessibility(input_filename):
    with open(input_filename, 'r', encoding='utf-8') as f:  # open in readonly mode
        tree = parse(f, parser=p)
        check_alt_text(tree)
        check_titles_and_captions(tree)
        check_vertical_text(tree)
        check_mark_labels(tree)


def check_mark_labels(tree):
    formats = tree.xpath("//worksheet[not(.//format[@attr='mark-labels-show'])]")
    for format in formats:
        sheet = get_parent_tag(format, 'worksheet').get("name")
        zones = tree.xpath("//zone[@name='"+sheet+"']")
        for zone in zones:
            if zone.get('_.fcp.SetMembershipControl.false...type') is None:
                dashboard_name = get_parent_dashboard(zone)
                print("B3 no mark labels for view '"+sheet+"' in dashboard '"+dashboard_name+"'")


def check_vertical_text(tree):
    formats = tree.xpath("//format[@attr='text-orientation' and (@value='-90' or @value='90')]")
    for format in formats:
        sheet = get_parent_tag(format, 'worksheet').get("name")
        zones = tree.xpath("//zone[@name='"+sheet+"']")
        for zone in zones:
            if zone.get('_.fcp.SetMembershipControl.false...type') is None:
                dashboard_name = get_parent_dashboard(zone)
                print("B1 text is rotated for view '"+sheet+"' in dashboard '"+dashboard_name+"'")


def check_alt_text(tree):
    images = tree.xpath("//zone[@_.fcp.SetMembershipControl.false...type='bitmap']")
    for image in images:
        if not image.get("alt-text") or image.get("alt-text") == '':
            print("A4 image with missing alternative text in dashboard '"+get_parent_dashboard(image) + "'")


def check_titles_and_captions(tree):
    zones = tree.xpath("//zone[@name]")
    for zone in zones:
        if zone.get('_.fcp.SetMembershipControl.false...type') is None:
            dashboard_name = get_parent_dashboard(zone)
            item = zone.get('name')
            if zone.get('show-title') and zone.get('show-title') == 'false':
                print("A5 Object '" + item + "' in dashboard '" + dashboard_name + "' has no title")
            if not zone.get('show-caption') or zone.get('show-caption') == 'false':
                print("A6 Object '" + item + "' in dashboard '" + dashboard_name + "' has no caption")


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
                if zone is not None:
                    zone.set("id", zone_id.__str__())
                    zone.set("is-modified", '1')
                    zone_id += 1
                else:
                    print("Error in manifest: object '"+item+"' does not exist in dashboard '"+dashboard_name+"'")

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

    argparser = argparse.ArgumentParser(description='Accessibility testing and tab focus order fixer for Tableau.')
    argparser.add_argument('input_path', metavar='I', type=str, nargs=1, default='testing.twb',
                        help='The name of the Tableau file to process')
    argparser.add_argument('output_path', metavar='O', type=str, nargs=1, default='output.twb',
                        help='The output file name')
    argparser.add_argument('manifest_path', metavar='M', type=str, nargs=1, default='manifest.txt',
                        help='The manifest file')
    argparser.add_argument('-t', action='store_true',
                        help='Just check for issues without modifying focus order')

    args = argparser.parse_args()

    # Defaults
    input_path = vars(args)['input_path'][0]
    output_path = vars(args)['output_path'][0]
    manifest_path = vars(args)['manifest_path'][0]
    check_only = vars(args)['t']

    if check_only:
        print("Only checking for issues, will not create output")
    else:
        print("Modifying tab order and checking issues")

    if not os.path.exists(input_path):
        print('Input workbook does not exist')
        exit()
    else:
        print("Input workbook: "+input_path)

    print("Output workbook: "+output_path)

    if not os.path.exists(manifest_path) and not check_only:
        print('Manifest does not exist')
        exit()
    else:
        print("Manifest: "+manifest_path)

    # Load the configuration/manifest
    if not check_only:
        with open(manifest_path, 'r') as file:
            configuration = load(file, Loader=loader.SafeLoader)
            fix_tabs(input_path, output_path, configuration)

    check_accessibility(input_path)

