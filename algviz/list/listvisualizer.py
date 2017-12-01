import svgwrite
from .const import WIDTH, HEIGHT


class ListVisualizer:
    def __init__(
            self, filename, List, canvasParams,
            customItemMeasurements=(None, None)):
        """
        filename is the name of the outputted svg file
        List is the list to visualize
        canvasParams is tuple: (width, height)

        Makes a file
        """
        self._list = List
        self._canvasParams = canvasParams
        self._canvas = svgwrite.Drawing(filename, canvasParams)
        self._customItemMeasurements = customItemMeasurements
        self._draw()
        self._canvas.save()

    def _draw(self):
        """
        Draws the list in self._list

        Returns void
        """
        widthPerListItem, heightPerListItem = self._listItemMeasurements()
        firstXCoordinate, firstYCoordinate = 0, 0

        for i, value in enumerate(self._list):
            newRectXCoordinate = firstXCoordinate + i*(widthPerListItem)
            recInsertPoint = (newRectXCoordinate, firstYCoordinate)
            recInsertSize = (widthPerListItem, heightPerListItem)
            rectangleToAdd = svgwrite.shapes.Rect(
                recInsertPoint,
                recInsertSize,
                stroke_width='3',
                stroke='black',
                fill='white')
            self._canvas.add(rectangleToAdd)

            # Interestingly, anything that appears in as an argument in the
            # text init function seems to appear as an attribute in the svg
            # description
            textXCoordinate = [recInsertPoint[0]+recInsertSize[0]/2]
            textYCoordinate = [recInsertPoint[1]+recInsertSize[1]/2]
            textValueToAdd = svgwrite.text.Text(
                text=str(value),
                x=textXCoordinate,
                y=textYCoordinate,
                # https://coderwall.com/p/a9nkrw/center-text-in-svg-rect-horz-and-vert
                text_anchor='middle',
                alignment_baseline='central',
                font_size=30)
            self._canvas.add(textValueToAdd)

    def _listItemMeasurements(self):
        """
        widthPerListItem = width of each list item
        heightPerListItem = height of each list item

        Custom measurements take precedence over calculated ones

        Returns Tuple: (widthPerListItem, heightPerListItem)
        """
        usableWidth = self._canvasParams[WIDTH]
        usableHeight = usableHeight = self._canvasParams[HEIGHT]

        customWidth = self._customItemMeasurements[WIDTH]
        calculatedWidth = usableWidth / len(self._list)
        widthPerListItem = customWidth if customWidth else calculatedWidth

        customHeight = self._customItemMeasurements[HEIGHT]
        heightPerListItem = customHeight if customHeight else usableHeight

        return widthPerListItem, heightPerListItem
