function newImage = border(Image, scaleFactor)
  height = size(Image,1);
  width = size(Image,2);
  
  Image(1:round(height*scaleFactor),:,:) = 0;			% Top border is zeroed
  Image(height-round(height*scaleFactor*6):height,:,:) = 0;	% Bottom border is zeroed
  Image(:,1:round(width*scaleFactor),:) = 0;			% Left border is zeroed
  Image(:,width-round(width*scaleFactor):width,:) = 0;		% Right border is zeroed

  newImage = Image;
end 
