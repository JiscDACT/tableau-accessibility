# SPDX-License-Identifier: MIT
import tabfix
import lxml
from lxml.etree import XMLParser, parse
import pytest
import os

p = XMLParser(huge_tree=True)

FIXTURE_DIR = os.path.dirname(os.path.realpath(__file__))


@pytest.fixture
def xml_files():
    return {
        1: parse(os.path.join(FIXTURE_DIR, 'testing.twb'), parser=p),
        2: parse(os.path.join(FIXTURE_DIR, 'testing_2019_4.twb'), parser=p)
    }


@pytest.fixture(params=[1, 2])
def xml_fixture(request, xml_files):
    """Parametrized backend instance."""
    return xml_files[request.param]


@pytest.fixture()
def xml_fixture_2020():
    return parse(os.path.join(FIXTURE_DIR, 'testing.twb'), parser=p)


def test_get_parent():
    tree = lxml.etree.fromstring("<apple><banana></banana></apple>")
    banana = tree.xpath("//banana")[0]
    apple = tabfix.get_parent_tag(banana, "apple")
    assert apple is not None
    assert apple.tag == 'apple'


def test_get_parent_dashboard():
    tree = lxml.etree.fromstring("<dashboard><a><banana></banana></a></dashboard>")
    banana = tree.xpath("//banana")[0]
    dashboard = tabfix.get_parent_dashboard(banana)
    assert dashboard is not None
    assert dashboard.tag == 'dashboard'


def test_get_parent_worksheet():
    tree = lxml.etree.fromstring("<dashboard><worksheet><a><banana></banana></a></worksheet></dashboard>")
    banana = tree.xpath("//banana")[0]
    sheet = tabfix.get_parent_worksheet(banana)
    assert sheet is not None
    assert sheet.tag == 'worksheet'


def test_get_highlighter_by_filter(xml_fixture_2020):
    assert tabfix.get_highlighter_by_filter(xml_fixture_2020, 'Dashboard', 'Highlight Region') is not None
    assert tabfix.get_highlighter_by_filter(xml_fixture_2020, 'Dashboard', 'Highlight Region').__len__() == 1
    assert tabfix.get_highlighter_by_filter(xml_fixture_2020, 'Dashboard', 'Highlight Region').tag == 'zone'
    assert tabfix.get_highlighter_by_filter(xml_fixture_2020, 'Dashboard', 'Region') is None


def test_get_highlighter(xml_fixture_2020):
    assert tabfix.get_item(xml_fixture_2020, "Dashboard", "Highlight Region") is not None
    assert(tabfix.get_item(xml_fixture_2020, "Dashboard", "Highlight Region").
           get("_.fcp.SetMembershipControl.false...type") == "highlighter")
    assert tabfix.get_item(xml_fixture_2020, "Dashboard", "Region") is not None
    assert(tabfix.get_item(xml_fixture_2020, "Dashboard", "Region").
           get("_.fcp.SetMembershipControl.false...type") != "highlighter")


def test_get_view(xml_fixture):
    assert tabfix.get_view(xml_fixture, 'Dashboard', 'Pie') is not None
    assert tabfix.get_view(xml_fixture, 'Dashboard', 'Pie').__len__() == 1
    assert tabfix.get_view(xml_fixture, 'Dashboard', 'Pie').tag == 'zone'

    assert tabfix.get_view(xml_fixture, 'Other Dashboard', 'Bar Without Mark Labels') is not None
    assert tabfix.get_view(xml_fixture, 'Other Dashboard', 'Bar Without Mark Labels').__len__() == 1
    assert tabfix.get_view(xml_fixture, 'Other Dashboard', 'Bar Without Mark Labels').tag == 'zone'

    # This is a button
    assert tabfix.get_view(xml_fixture, 'Dashboard', 'The First Parameter') is None
    assert tabfix.get_view(xml_fixture, 'Dashboard', 'navigate to other dashboard') is None


def test_get_button(xml_fixture):
    assert tabfix.get_button(xml_fixture, 'Dashboard', 'navigate to other dashboard') is not None
    assert tabfix.get_button(xml_fixture, 'Dashboard', 'navigate to other dashboard').tag == 'zone'
    assert tabfix.get_button(xml_fixture, 'Dashboard', 'fake button') is None
    # This is a view
    assert tabfix.get_button(xml_fixture, 'Dashboard', 'Pie') is None


def test_get_parameter_by_name(xml_fixture):
    assert tabfix.get_parameter(xml_fixture, 'Dashboard', 'Parameter 1 Name') is not None
    assert tabfix.get_parameter(xml_fixture, 'Dashboard', 'Parameter 1 Name').tag == 'zone'
    assert tabfix.get_parameter(xml_fixture, 'Dashboard', 'fake parameter') is None
    # This is a view
    assert tabfix.get_parameter(xml_fixture, 'Dashboard', 'Pie') is None
    # This is a filter
    assert tabfix.get_parameter(xml_fixture, 'Dashboard', 'Region') is None


def test_get_parameter_by_title(xml_fixture):
    assert tabfix.get_parameter(xml_fixture, 'Dashboard', 'Parameter 1 Title') is not None
    assert tabfix.get_parameter(xml_fixture, 'Dashboard', 'Parameter 1 Title').tag == 'zone'
    assert tabfix.get_parameter(xml_fixture, 'Dashboard', 'fake parameter') is None
    # This is a view
    assert tabfix.get_parameter(xml_fixture, 'Dashboard', 'Pie') is None
    # This is a filter
    assert tabfix.get_parameter(xml_fixture, 'Dashboard', 'Region') is None


def test_get_filter(xml_fixture):
    assert tabfix.get_filter(xml_fixture, 'Dashboard', 'Region') is not None
    assert tabfix.get_filter(xml_fixture, 'Dashboard', 'Region').tag == 'zone'
    assert tabfix.get_filter(xml_fixture, 'Dashboard', 'fake filter') is None
    # This is a view
    assert tabfix.get_filter(xml_fixture, 'Dashboard', 'Pie') is None
    # This is a parameter
    assert tabfix.get_filter(xml_fixture, 'Dashboard', 'Parameter 1') is None


def test_get_image(xml_fixture):
    assert tabfix.get_image(xml_fixture, 'Dashboard', '1114.jpg') is not None
    assert tabfix.get_image(xml_fixture, 'Dashboard', '1114.jpg').tag == 'zone'
    assert tabfix.get_image(xml_fixture, 'Dashboard', 'fake filter') is None
    # This is a view
    assert tabfix.get_image(xml_fixture, 'Dashboard', 'Pie') is None
    # This is a parameter
    assert tabfix.get_image(xml_fixture, 'Dashboard', 'Parameter 1') is None


def test_check_mark_labels(xml_fixture):
    assert tabfix.check_mark_labels(xml_fixture) is not None
    assert tabfix.check_mark_labels(xml_fixture).__len__() == 3
    for warning in tabfix.check_mark_labels(xml_fixture):
        assert warning.get("item") in ["Bar Without Mark Labels", "Pie"]


def test_check_vertical_text(xml_fixture):
    assert tabfix.check_vertical_text(xml_fixture) is not None
    assert tabfix.check_vertical_text(xml_fixture).__len__() == 2
    for warning in tabfix.check_vertical_text(xml_fixture):
        assert warning.get("item") in ["Bar Without Mark Labels", "Bar With Mark Labels"]


def test_check_alt_text(xml_fixture):
    assert tabfix.check_alt_text(xml_fixture) is not None
    assert 1 == tabfix.check_alt_text(xml_fixture).__len__()
    for warning in tabfix.check_alt_text(xml_fixture):
        assert warning.get("dashboard") in ["Dashboard"]


def test_check_titles_and_captions(xml_fixture):
    assert tabfix.check_titles_and_captions(xml_fixture) is not None
    assert 4 == tabfix.check_titles_and_captions(xml_fixture).__len__()
    for warning in tabfix.check_titles_and_captions(xml_fixture):
        assert warning.get("item") in ["Bar Without Mark Labels", "Pie", "Sheet 3"]
        assert (warning.get("code") == 'A5' and warning.get("item") in ["Pie", "Sheet 3"]) or warning.get("code") == 'A6'
        assert (warning.get("code") == 'A6' and warning.get("item") in ["Bar Without Mark Labels", "Sheet 3"]) or warning.get("code") == 'A5'


def test_load_manifest():
    assert tabfix.load_manifest(os.path.join(FIXTURE_DIR, 'manifest.yaml')) is not None


def test_fix_tabs(xml_fixture):
    configuration = {"Dashboard": ["Region", "Pie"]}
    tree = tabfix.fix_tabs_in_tree(xml_fixture, configuration)
    region = tabfix.get_item(tree, "Dashboard", "Region")
    pie = tabfix.get_item(tree, "Dashboard", "Pie")
    assert "100" == region.get("id")
    assert "101" == pie.get("id")

    configuration = {"Dashboard": ["Pie", "Region"]}
    tree = tabfix.fix_tabs_in_tree(xml_fixture, configuration)
    region = tabfix.get_item(tree, "Dashboard", "Region")
    pie = tabfix.get_item(tree, "Dashboard", "Pie")
    assert "101" == region.get("id")
    assert "100" == pie.get("id")

    configuration = {"Dashboard": ["Pie", "Parameter 2", "Region"]}
    tree = tabfix.fix_tabs_in_tree(xml_fixture, configuration)
    p2 = tabfix.get_item(tree, "Dashboard", "Parameter 2")
    region = tabfix.get_item(tree, "Dashboard", "Region")
    pie = tabfix.get_item(tree, "Dashboard", "Pie")
    assert "100" == pie.get("id")
    assert "101" == p2.get("id")
    assert "102" == region.get("id")


def test_fix_tabs_2(xml_fixture_2020):
    configuration = {"Dashboard": ["Parameter 1 Name", "Parameter 2"]}
    tree = tabfix.fix_tabs_in_tree(xml_fixture_2020, configuration)
    p2 = tabfix.get_item(tree, "Dashboard", "Parameter 2")
    p1 = tabfix.get_item(tree, "Dashboard", "Parameter 1 Name")
    assert "101" == p2.get("id")
    assert "100" == p1.get("id")

