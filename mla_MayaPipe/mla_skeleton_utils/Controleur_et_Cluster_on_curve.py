#----------------------Par Christelle GIBOIN ----------------------
# automatic place 
#_Place_le pivot au debut des curve
#_mettre les Cluster et les controlers sur la curve


import maya.cmds as cmds
import random

Selection = cmds.ls( orderedSelection=True )
NombreCurve = len(Selection)


#------------BOITE DE DIALOGUE -------------------
# Pour definir la forme des controleurs des Cluster
     
 
result = cmds.promptDialog(
        title='Nom Controleur',
	    message='Entrer le nom du Controleur que vous souhaitez utiliser pour.',    
	    button=['OK', 'Cancel'],
	    defaultButton='OK',
	    cancelButton='Cancel',
	    dismissString='Cancel')

if result == 'OK':
	        FormeCtrl = cmds.promptDialog(query=True, text=True)
	
else :
            Anulation = cmds.confirmDialog(
            title='Confirm', 
            message='Vous devez cr�er un controleur qui g�rera les clusters', 
            button=['Yes'], 
            defaultButton='Yes')

            
#---------------------------------------------------------
#--------------------------------------------------------- 


for i in range( 0 , NombreCurve ) : 

    NomCurve = Selection[i]
    
    #_recuperation du nom de la shape
    cmds.select( NomCurve )
    cmds.pickWalk( direction='down' )
    SelectionShape = cmds.ls( sl = True )
    NomCurveShape = SelectionShape[0]
    
    print(NomCurve)
    print(NomCurveShape)
    
    # Placement du Pivot au debut de la curve
    CurveInf = cmds.createNode( 'curveInfo' ) # Cree un node curveInfo -> Utile !!
    CurveInf = cmds.rename( CurveInf , NomCurve + 'Curve_Info' )
    cmds.connectAttr( NomCurveShape + '.worldSpace', CurveInf + '.inputCurve' )
    
    PositionCvX = cmds.getAttr( CurveInf + '.controlPoints[0].xValue' )
    PositionCvY = cmds.getAttr( CurveInf + '.controlPoints[0].yValue' )
    PositionCvZ = cmds.getAttr( CurveInf + '.controlPoints[0].zValue' )
    
    cmds.move( PositionCvX , PositionCvY , PositionCvZ , NomCurve + '.scalePivot' , NomCurve + '.rotatePivot' , absolute = True ) 
    
    
    #----------------------------
    #_Creation des cluster su chaque CV
    
    DegreeCurve = cmds.getAttr( NomCurveShape + '.degree' )
    SpanCurve = cmds.getAttr( NomCurveShape + '.spans' )
    
    NombreCv = DegreeCurve + SpanCurve
    
    print( NombreCv )
    
    
    for j in range( 0 , NombreCv ) :
      
        #Creation des clusters :)
              
        nombre = str(j)
        NomCluster = ( NomCurve + '.cv[' + nombre + ']' )
        print(NomCluster)
    
        cmds.select( NomCluster )
        Cluster = cmds.cluster()
        
        cmds.select( deselect = True )
        
        #_Recuperation de la position des Cluster
        PositionClusterX = cmds.getAttr( CurveInf + '.controlPoints[' + nombre + '].xValue' )
        PositionClusterY = cmds.getAttr( CurveInf + '.controlPoints[' + nombre + '].yValue' )
        PositionClusterZ = cmds.getAttr( CurveInf + '.controlPoints[' + nombre + '].zValue' )
        print(PositionClusterX)
        print(PositionClusterY)
        print(PositionClusterZ)
        
        #------------------------------------------------------
        # Creation des Controleurs
        
        cmds.select(FormeCtrl)
        CtrlCLuster = cmds.duplicate(FormeCtrl)
        CtrlCLuster = cmds.rename( CtrlCLuster , 'CTRL_' + NomCurve + '_' + nombre )
        cmds.move( PositionClusterX , PositionClusterY , PositionClusterZ , CtrlCLuster , absolute = True )
        
        #_Ofset des controleur ------------------
        
        GrOfset = cmds.group( em=True, name= CtrlCLuster + '_Offset' )
        Constraint = cmds.parentConstraint( CtrlCLuster , GrOfset )
        cmds.delete(Constraint)
        cmds.parent( CtrlCLuster, GrOfset )
        
        # ---------------------------------------------------------------
        
        
        #_Parente des Cluster sur les controleurs
        
        cmds.parent( Cluster , CtrlCLuster )
        
        #---
        

    cmds.select( 'CTRL_' + NomCurve + '_*_Offset' )
    cmds.group( name= 'Group_CTRL_' + NomCurve )
    cmds.select( deselect = True )
        #------------------------------------------------------------------
        #------------------------------------------------------------------
        
#--------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------
