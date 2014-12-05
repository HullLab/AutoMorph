function newBoxes = expandBoundingBox(Boxes, scaleFactor, Isize)

  size(Boxes);

  numBoxes = length(Boxes);
  for bLoop = 1:numBoxes

    CurrentBox = Boxes(bLoop).BoundingBox;

    % X-coordinate of bounding box's upper left corner - (width of region*scaleFactor)
    newLeft = CurrentBox(1) - round(CurrentBox(3) * scaleFactor);
    if (newLeft < 1)	
      newLeft = 1;
    end

    % Y-coordinate of bounding box's upper left corner - (height of region*scaleFactor)
    newTop  = CurrentBox(2) - round(CurrentBox(4) * scaleFactor);
    if (newTop < 1)		% Verify we don't pass the top edge of the image
      newTop = 1;
    end

    % X-width of bounding box - width+(2*width*scaleFactor)
    newWidth = CurrentBox(3) + round(CurrentBox(3) * 2 * scaleFactor);
    if (newWidth > Isize(1))
       newWidth = Isize(1);
    end

    % Y-height of bounding box - height+(2*height*scaleFactor)
    newHeight = CurrentBox(4) + round(CurrentBox(4) * 2 * scaleFactor);
    if (newHeight > Isize(2))
       newHeight = Isize(2);
    end

    newBox = [newLeft newTop newWidth newHeight];
    Boxes(bLoop).BoundingBox = newBox;
  end

  newBoxes = Boxes;
end

