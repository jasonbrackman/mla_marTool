import mla_Multi_import_utils as import_utils

application, mc, api = import_utils.import_from_application()

if application == 'Maya':
    import mla_MayaPipe.mla_rendering_utils.mla_shading_utils as su


def open_file(filepath):
    if application == 'Maya':
        mc.file(filepath, o=True, usingNamespaces=False, f=True)
    elif application == 'Max':
        pass
    else:
        pass


def save_file(filepath):
    if 'untitled' in filepath:
        print 'Cannot save an untitled scene.'
        return
    else:
        if application == 'Maya':
            mc.file(rename=filepath)
            if filepath.split('.')[-1] == 'mb':
                filetype = 'mayaBinary'
            else:
                filetype = 'mayaAscii'
            mc.file(s=True, type=filetype, f=True)
        elif application == 'Max':
            pass
        else:
            pass


def reference_file(filepath):
    if application == 'Maya':
        mc.file(filepath, r=True, usingNamespaces=False, f=True)
    elif application == 'Max':
        pass
    else:
        pass


def import_scene_file(filepath):
    if application == 'Maya':
        mc.file(filepath, i=True, usingNamespaces=False, f=True)
    elif application == 'Max':
        pass
    else:
        pass


def save_screenshot(filepath):
    if application == 'Maya':
        mc.setAttr('defaultRenderGlobals.imageFormat', 8)

        mc.playblast(completeFilename=filepath, forceOverwrite=True,
                     format='image', width=512, height=512, showOrnaments=False,
                     startTime=1, endTime=1, viewer=False)
    elif application == 'Max':
        pass
    else:
        pass


def import_image_file(filepath):
    if application == 'Maya':
        file_node = su.create_file_node_setup()

        mc.setAttr('%s.fileTextureName' % file_node, filepath)
        return file_node
    elif application == 'Max':
        pass
    else:
        pass


def import_sound_file(filepath, sound):
    if application == 'Maya':
        if not mc.objExists('%s_sound' % sound):
            current_time = mc.currentTime(q=True)

            mc.sound(n='%s_sound' % sound, f=filepath, o=current_time)
            return '%s_sound' % sound
        else:
            print "This audio file is already in the scene."
            return
    elif application == 'Max':
        pass
    else:
        pass
