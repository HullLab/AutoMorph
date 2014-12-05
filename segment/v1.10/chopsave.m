    
function chopsave(orgIMAGE, BOXES, Llist, Slist,pixLim,nameEm)
    
    boxNum = length(BOXES);
    tick=1;     % increments object names
    for segChop = 1:boxNum   
        
        if ((Slist(segChop)<1)==1)
            if ((Llist(segChop, 1)>pixLim)==1)
                subImage = orgIMAGE(round(BOXES(segChop).BoundingBox(2):BOXES(segChop).BoundingBox(2)...
            +BOXES(segChop).BoundingBox(4)), round(BOXES(segChop).BoundingBox(1):...
            BOXES(segChop).BoundingBox(1)+BOXES(segChop).BoundingBox(3)),:);
            
                fileName=strcat(nameEm,'_obj',sprintf('%05.0f',tick),'.tif');
                imwrite (subImage,fileName, 'tif') 
                tick=tick+1;
            end
        end
    end
end