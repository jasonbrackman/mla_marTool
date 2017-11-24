import maya.cmds as mc

selection = mc.ls(sl=True, fl=True)

selection_length = len(selection)

i=0
for object in selection:
    nameMult = "MULT_" + object
    myShader = mc.shadingNode('multiplyDivide', n=nameMult, au=True)
    mc.connectAttr(object + ".translate", nameMult + ".input1")
    mc.setAttr(nameMult + ".input2", -1, -1, -1)
    mc.connectAttr(nameMult + ".output", object + "_orig.translate")
    i+=1