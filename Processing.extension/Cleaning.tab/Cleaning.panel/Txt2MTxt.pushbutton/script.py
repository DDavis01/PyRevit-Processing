# Importing necessary modules
from Autodesk.Revit.DB import XYZ, Transaction, BuiltInParameter, TextNoteType # type: ignore
from pyrevit import revit, DB # type: ignore
# Get the active document and UIDocument
doc = __revit__.ActiveUIDocument.Document # type: ignore
uidoc = __revit__.ActiveUIDocument # type: ignore

# Get the element selection of the current document
selection = uidoc.Selection

# Store element ids
selectedIds = uidoc.Selection.GetElementIds()

# Make a list for holding items that are not text notes, so they are not deleted
mylist = []

# Create a list to hold the text strings
textStrings = []

# Go through each selected item
for id in selectedIds:
    # Get the element from the id
    e = doc.GetElement(id)

    try:
        # Check if the element has a text parameter
        if e.get_Parameter(BuiltInParameter.TEXT_TEXT):
            # Get the text parameter and the text contained in the parameter
            myTextParam = e.get_Parameter(BuiltInParameter.TEXT_TEXT)
            myText = myTextParam.AsString()

            # Cast the element as a TextNote so the coordinates can be obtained
            t = e if isinstance(e, DB.TextNote) else None
            if t is not None:
                textStrings.append(myText)
            else:
                mylist.append(id)
                print("Element with ID {0} is not a TextNote.".format(id))
        else:
            print("Element with ID {0} does not have a text parameter.".format(id))

    # If an item is not a text note, it should be caught here
    except Exception as ex:
        print("Exception: {0}".format(ex))
        mylist.append(id)

# Combine text strings into one multiline text
combinedText = '\n'.join(textStrings)

# Create a new multiline text note at the location of the first selected text note
if len(textStrings) > 0:
    firstTextNoteId = selectedIds[0]  # Get the first element ID from the list
    firstTextNote = doc.GetElement(firstTextNoteId)
    textLocation = firstTextNote.Coord
    textTypeId = firstTextNote.GetTypeId()
    
    # Start a transaction to create a new multiline text note
    with Transaction(doc, "Combine Text Notes") as transaction:
        transaction.Start()
        
        # Create a new multiline text note
        newTextNote = DB.TextNote.Create(doc, doc.ActiveView.Id, textLocation, combinedText, textTypeId)
        
        # Delete the old text notes
        for oldTextNoteId in selectedIds:
            doc.Delete(oldTextNoteId)
        
        transaction.Commit()

    print("Text notes combined into a new multiline text note, and old text notes deleted.")
else:
    print("No text notes selected.")
print("\nNot Text Ids:")
print(mylist)