# Tabfix

*A command-line tool for improving Tableau accessibility*

## How does it work?
Tabfix inspects the Tableau XML file (.twb) and checks a number of assertions related to accessibility, 
such as whether a worksheet has a title and caption, whether any text is displayed
vertically, or if images lack alternative text.

## Installing
To install the pre-built .exe on Windows, 
download it and add the location to your system Path.

## Running
Either run the pre-built tabfix.exe from the command line, or run the script
using Python.

### Usage - setting  keyboard navigation order
Before running Tabfix, create a file called manifest.yaml in the same folder as your Tableau workbook. Edit this file and create the tab order you want the workbook to use. For example: 
~~~
Dashboard:
- Region
- Parameter 2
- Parameter 1
- Pie
- Bar
Other Dashboard:
- Parameter 1
- Parameter 2
- Pie
- Bar
- Region
~~~


Each dashboard name must be on a newline ending in a colon. Each dashboard item must be on a new line starting with a dash and space. 

You may use view names, filter names, and parameter names. Note that names that begin with numbers or symbols such as '%' should be enclosed in quotes. 

For buttons, use the button label rather than "Button". 

Tableau does not provide keyboard access to text objects or images. 

You run Tabfix from the Windows command prompt (CMD).  You can quickly open this by right-clicking the Windows icon in the bottom-right of the screen. 

Navigate to the folder containing your workbook, and enter: 

`tabfix your-workbook-name.twb manifest.yaml`

By default, Tabfix will output the results in a new workbook, output.twb, using the specification in manifest.txt. 

Note that if your workbook name contains spaces, you should enclose it in quotation marks. 


### Usage – testing for accessibility issues 
You can run tabfix to just check accessibility issues. To do this, navigate to the folder containing your workbook, and enter: 

`tabfix your-workbook-name.twb -t `


### Usage – accessiblity report in CSV format 
You can output the results of the accessibility check in CSV format. To do this, use the –c option, e.g.: 

`tabfix your-workbook-name.twb -t -c `

The report will be saved as accessibility_report.csv in your current folder. 

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
You can use a manifest file in YAML format to specify the focus order
for a dashboard. There is an example of a manifest file in the test subfolder.

For most dashboard items you can use either the name or title of the item; view names, 
filter titles, parameter names and so on. For images that use links, you need to use
the image filename. For highlighters, use "Highlight" with an associated filter name, 
e.g. "Highlight Region".

This can cause problems if, for example, a filter and a parameter have the same name. 
You'll need to rename one of them to prevent a clash.

## Known issues and limitations
Tabfix currently has problems with fixing the focus order where there are 
device layouts, and outputs the modified .twb without device layouts.

Tabfix can't open packaged workbooks (.twbx), only .twb files.