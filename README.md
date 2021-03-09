# Tabfix

*A command-line tool for Tableau accessibility*

## How does it work?
Tabfix inspects the Tableau XML file (.twb) and checks a number of assertions related to accessibility, 
such as whether a worksheet has a title and caption, whether any text is displayed
vertically, or if images lack alternative text.

## Installing

## Running

## Tableau accessibility issues

Issue | Description
----- | -----
A1 | Tab order: Each dashboard needs to have a logical focus order for keyboard or clicker navigation. 
A2 | Colour contrast:  Sufficient contrast and colour-blind safe colours 
A3 | >1000 data points: Prevent server-side rendering 
A4 | Images with missing or incorrect alternative text 
A5 | Titles: All dashboards have a title 
A6 | Captions: All data views have a caption or title 
A7 | Alternative representation – data download: Data can be downloaded for the view e.g. View Data is enabled 
B1 | Readable text: Labels are not vertical 
B2 | Tooltips: Tooltips should provide supplemental, not essential data. 
B3 | Mark labels: Marks have meaningful labels rather than rely on visual judgement alone (e.g. bar length) 
B4 | Navigation and context: Navigation is clear and contains breadcrumb or similar context cues 
B5 | Colour used as only differentiator 
B6 | Interactions are understandable: Interactions are explained in text, e.g. filter actions 

## What does Tabfix check for?
Tabfix can check for issues A4, A5, A6, B1, and B3. This doesn't mean you
should rely on it solely for testing for these issues - its possible to
include meaningless captions for example - but it provides a quick way of
assessing the scale of accessibility work needed.

## What doesn't Tabfix check?
Tabfix can't check for A1, but it can change the focus order (see below).

Tabfix can't currently check A2, A3, A7, B2, B4, B5 and B6.

It may be possible in future to extend Tabfix to check A2 and B5.

## Specifying the focus order using a manifest file

## Known issues and limitations
Tabfix currently has problems with fixing the focus order where there are 
device layouts, and outputs the modified .twb without device layouts.

Tabfix can't open packaged workbooks (.twbx), only .twb files.