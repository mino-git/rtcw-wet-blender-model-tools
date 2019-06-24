
import math

import bpy
import mathutils


def test_case_1():
    """Create an edit bone using head, tail and roll.
    """

    # create a collection
    collection = bpy.data.collections.new("Collection")
    bpy.context.scene.collection.children.link(collection)

    # create an armature
    armature = bpy.data.armatures.new("Armature")
    armature_object = bpy.data.objects.new(armature.name, armature)
    collection.objects.link(armature_object)

   # switch to edit mode
    bpy.context.view_layer.objects.active = \
        bpy.data.objects[armature_object.name]
    bpy.ops.object.mode_set(mode='EDIT')

    # create edit_bone_1
    edit_bone_1 = armature_object.data.edit_bones.new("TestBone1")

    # set the bones location and orientation
    # the coordinates are given in armature space
    edit_bone_1.head = (0, 1, 0)
    edit_bone_1.tail = (0, 1, 1)
    edit_bone_1.roll = math.radians(45.0)

    # switch back to object mode
    bpy.ops.object.mode_set(mode='OBJECT')


def test_case_2():
    """Create an edit bone using matrix.
    """

    # create a collection
    collection = bpy.data.collections.new("Collection")
    bpy.context.scene.collection.children.link(collection)

    # create an armature
    armature = bpy.data.armatures.new("Armature")
    armature_object = bpy.data.objects.new(armature.name, armature)
    collection.objects.link(armature_object)

   # switch to edit mode
    bpy.context.view_layer.objects.active = \
        bpy.data.objects[armature_object.name]
    bpy.ops.object.mode_set(mode='EDIT')

    # create edit_bone_1
    edit_bone_1 = armature_object.data.edit_bones.new("TestBone1")

    # set the bones head and tail (still required so the bone is scaled)
    edit_bone_1.head = (0, 0, 0)
    edit_bone_1.tail = (1, 0, 0)

    # use matrix to set location and orientation
    # the coordinates are given in armature space
    edit_bone_1.matrix = mathutils.Matrix.Identity(4)

    # note: setting head and tail AFTER the matrix is set will overwrite the
    # matrix values again

    # switch back to object mode
    bpy.ops.object.mode_set(mode='OBJECT')


def test_case_3():
    """Create a bone hierarchy.
    """

    # create a collection
    collection = bpy.data.collections.new("Collection")
    bpy.context.scene.collection.children.link(collection)

    # create an armature
    armature = bpy.data.armatures.new("Armature")
    armature_object = bpy.data.objects.new(armature.name, armature)
    collection.objects.link(armature_object)

   # switch to edit mode
    bpy.context.view_layer.objects.active = \
        bpy.data.objects[armature_object.name]
    bpy.ops.object.mode_set(mode='EDIT')

    # create the bones
    edit_bone_1 = armature_object.data.edit_bones.new("TestBone1")
    edit_bone_2 = armature_object.data.edit_bones.new("TestBone2")
    edit_bone_3 = armature_object.data.edit_bones.new("TestBone3")

    # set parent-child-relations
    edit_bone_3.parent = edit_bone_2
    edit_bone_2.parent = edit_bone_1

    # set the bones locations and orientations
    edit_bone_1.head = (0, 0, 0)
    edit_bone_1.tail = (1, 0, 0)
    location = mathutils.Matrix.Translation((0, 1, 0))
    orientation = mathutils.Euler((math.radians(90.0), 0.0, 0.0), 'XYZ').to_matrix().to_4x4()
    edit_bone_1.matrix = location @ orientation

    edit_bone_2.head = (0, 0, 0)
    edit_bone_2.tail = (1, 0, 0)
    location = mathutils.Matrix.Translation((0, 2, 0))
    orientation = mathutils.Euler((0.0, math.radians(90.0), 0.0), 'XYZ').to_matrix().to_4x4()
    edit_bone_2.matrix = location @ orientation

    edit_bone_3.head = (0, 0, 0)
    edit_bone_3.tail = (1, 0, 0)
    location = mathutils.Matrix.Translation((0, 3, 0))
    orientation = mathutils.Euler((0.0, 0.0, math.radians(90.0)), 'XYZ').to_matrix().to_4x4()
    edit_bone_3.matrix = location @ orientation

    # switch back to object mode
    bpy.ops.object.mode_set(mode='OBJECT')

def test_case_4():
    """Animate the bone hierarchy.
    """

    # create a collection
    collection = bpy.data.collections.new("Collection")
    bpy.context.scene.collection.children.link(collection)

    # create an armature
    armature = bpy.data.armatures.new("Armature")
    armature_object = bpy.data.objects.new(armature.name, armature)
    collection.objects.link(armature_object)

   # switch to edit mode
    bpy.context.view_layer.objects.active = \
        bpy.data.objects[armature_object.name]
    bpy.ops.object.mode_set(mode='EDIT')

    # create the bones
    edit_bone_1 = armature_object.data.edit_bones.new("TestBone1")
    edit_bone_2 = armature_object.data.edit_bones.new("TestBone2")
    edit_bone_3 = armature_object.data.edit_bones.new("TestBone3")

    # set parent-child-relations
    edit_bone_3.parent = edit_bone_2
    edit_bone_2.parent = edit_bone_1

    # set the bones locations and orientations
    edit_bone_1.head = (0, 0, 0)
    edit_bone_1.tail = (1, 0, 0)
    location = mathutils.Matrix.Translation((0, 1, 0))
    orientation = mathutils.Euler((math.radians(90.0), 0.0, 0.0), 'ZYX').to_matrix().to_4x4()
    edit_bone_1.matrix = location @ orientation

    edit_bone_2.head = (0, 0, 0)
    edit_bone_2.tail = (1, 0, 0)
    location = mathutils.Matrix.Translation((0, 2, 0))
    orientation = mathutils.Euler((math.radians(90.0), 0, math.radians(90.0)), 'ZYX').to_matrix().to_4x4()
    edit_bone_2.matrix = location @ orientation

    edit_bone_3.head = (0, 0, 0)
    edit_bone_3.tail = (1, 0, 0)
    location = mathutils.Matrix.Translation((0, 3, 0))
    orientation = mathutils.Euler((0.0, 0.0, math.radians(90.0)), 'ZYX').to_matrix().to_4x4()
    edit_bone_3.matrix = location @ orientation

    # switch back to pose mode
    bpy.ops.object.mode_set(mode='POSE')

    # armature_object.animation_data_create()
    # armature_object.animation_data.action = \
    #     bpy.data.actions.new(name=armature_object.name)

    pose_bone_1 = armature_object.pose.bones["TestBone1"]
    pose_bone_2 = armature_object.pose.bones["TestBone2"]
    pose_bone_3 = armature_object.pose.bones["TestBone3"]

    pose_bone_1.rotation_mode = 'ZYX'
    pose_bone_2.rotation_mode = 'ZYX'
    pose_bone_3.rotation_mode = 'ZYX'

def random_test():

    # test_case_1()
    # test_case_2()
    # test_case_3()
    test_case_4()


# edit_bone_1.matrix = mathutils.Matrix.Identity(4)

# all bone locs/rots extraction to internal format

# make 2 frame skeleton

# def create_edit_bones(armature_object):

#     bpy.context.view_layer.objects.active = \
#         bpy.data.objects[armature_object.name]
#     bpy.ops.object.mode_set(mode='EDIT')

#     # TestBone1
#     edit_bone_1 = armature_object.data.edit_bones.new("TestBone1")
#     edit_bone_1.head = (0, 0, 0)
#     edit_bone_1.tail = (0, 1, 0)
#     edit_bone_1.use_connect = False
#     edit_bone_1.use_inherit_scale = True
#     edit_bone_1.use_local_location = True
#     edit_bone_1.use_inherit_rotation = True

#     location = mathutils.Vector((0, 1, 0))
#     orientation = mathutils.Matrix.Rotation(math.radians(45.0), 4, 'X')

#     matrix = mathutils.Matrix.Translation(location)
#     edit_bone_1.matrix = matrix @ orientation

#     # TestBone2
#     edit_bone_2 = armature_object.data.edit_bones.new("TestBone2")
#     edit_bone_2.head = (0, 0, 0)
#     edit_bone_2.tail = (0, 1, 0)
#     edit_bone_2.use_connect = False
#     edit_bone_2.use_inherit_scale = True
#     edit_bone_2.use_local_location = True
#     edit_bone_2.use_inherit_rotation = True

#     location = mathutils.Vector((0, 2, 0))
#     orientation = mathutils.Matrix.Rotation(math.radians(0.0), 4, 'X')

#     matrix = mathutils.Matrix.Translation(location)
#     edit_bone_2.matrix = matrix @ orientation

#     edit_bone_2.parent = edit_bone_1

#     bpy.ops.object.mode_set(mode='OBJECT')
