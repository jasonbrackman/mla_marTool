import maya.cmds as mc

def create_cam_map_setup(fileslist, camera):
    # --- Loop for every file in the list
    for obj in fileslist:
        # --- Names
        diff_name = obj.split('.')[0]
        file_extension = obj.split('.')[1]
        alpha_name = diff_name.replace('_diff', '_alpha')
        lambert_name = diff_name.replace('_diff', '_lambert')
        diff = create_linear_setup(diff_name, file_extension, camera)
        alpha = create_linear_setup(alpha_name, file_extension, camera, alpha=True)
        # --- Create shading
        mc.shadingNode('lambert', asShader=True, n=lambert_name)
        mc.sets(renderable=True, noSurfaceShader=True, empty=True, name=lambert_name+'SG' )
        # --- Connect shading
        mc.connectAttr('%s.outColor' % lambert_name, '%sSG.surfaceShader' % lambert_name)
        # --- Connect setup to shading and set lambert
        mc.connectAttr('%s.outColor' % diff, '%s.color' % lambert_name)
        mc.connectAttr('%s.outColor' % alpha, '%s.transparency' % lambert_name)
        mc.setAttr('%s.ambientColor' % lambert_name, 1, 1, 1, type='double3')
        mc.setAttr('%s.diffuse' % lambert_name, 0)

def create_linear_setup(filename, file_extension, camera, alpha=False):
    filenode = filename+'_file'
    place2dnode = filename+'_place2dTexture'
    projnode = filename+'_projection'
    # --- Create nodes
    mc.shadingNode('place2dTexture', au=True, name=place2dnode)
    mc.shadingNode('file', at=True, name=filenode)
    mc.shadingNode('projection', au=True, name=projnode)
    # --- Connect and set them
    connect_place2dTexture_to_file(place2dnode, filenode)
    mc.setAttr('%s.wrapU' % place2dnode, 0)
    mc.setAttr('%s.wrapV' % place2dnode, 0)
    mc.connectAttr('%s.outColor' % filenode, '%s.image' % projnode)
    mc.setAttr('%s.fileTextureName' % filenode, '%s\\%s.%s' % (path, filename, file_extension), type='string')
    mc.setAttr('%s.defaultColor' % filenode, 0, 0, 0, type='double3')
    mc.setAttr('%s.projType' % projnode, 8)
    mc.connectAttr('%s.message' % camera, '%s.linkedCamera' % projnode)
    if alpha:
        mc.setAttr('%s.invert' % filenode, 1)

    return projnode

def connect_place2dTexture_to_file(place_Texture, filename):
    print place_Texture
    print filename
    mc.connectAttr('%s.coverage' % place_Texture, '%s.coverage' % filename)
    mc.connectAttr('%s.mirrorU' % place_Texture, '%s.mirrorU' % filename)
    mc.connectAttr('%s.mirrorV' % place_Texture, '%s.mirrorV' % filename)
    mc.connectAttr('%s.noiseUV' % place_Texture, '%s.noiseUV' % filename)
    mc.connectAttr('%s.offset' % place_Texture, '%s.offset' % filename)
    mc.connectAttr('%s.outUV' % place_Texture, '%s.uvCoord' % filename)
    mc.connectAttr('%s.outUvFilterSize' % place_Texture, '%s.uvFilterSize' % filename)
    mc.connectAttr('%s.repeatUV' % place_Texture, '%s.repeatUV' % filename)
    mc.connectAttr('%s.rotateFrame' % place_Texture, '%s.rotateFrame' % filename)
    mc.connectAttr('%s.rotateUV' % place_Texture, '%s.rotateUV' % filename)
    mc.connectAttr('%s.stagger' % place_Texture, '%s.stagger' % filename)
    mc.connectAttr('%s.translateFrame' % place_Texture, '%s.translateFrame' % filename)
    mc.connectAttr('%s.vertexCameraOne' % place_Texture, '%s.vertexCameraOne' % filename)
    mc.connectAttr('%s.vertexUvOne' % place_Texture, '%s.vertexUvOne' % filename)
    mc.connectAttr('%s.vertexUvTwo' % place_Texture, '%s.vertexUvTwo' % filename)
    mc.connectAttr('%s.vertexUvThree' % place_Texture, '%s.vertexUvThree' % filename)
    mc.connectAttr('%s.wrapU' % place_Texture, '%s.wrapU' % filename)
    mc.connectAttr('%s.wrapV' % place_Texture, '%s.wrapV' % filename)

def create_file_node_setup():
    file_node = mc.shadingNode('file', at=True)
    place2dTexture = mc.shadingNode('place2dTexture', at=True)

    connect_place2dTexture_to_file(place2dTexture, file_node)
    return file_node

