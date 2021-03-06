############################################################################
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <https://www.gnu.org/licenses/>.
############################################################################

import bpy, mathutils
from bpy.props import EnumProperty, BoolProperty
from bpy.types import Operator
from bsmax.state import has_constraint

# create a camera from view 
class Camera_OT_Create_From_View(Operator):
	bl_idname = "camera.create_from_view"
	bl_label = "Create Camera From View"
	bl_description = "Create New Camera From View"

	@classmethod
	def poll(self, ctx):
		return ctx.area.type == 'VIEW_3D'

	def execute(self, ctx):
		obj = ctx.selected_objects
		if len(obj) == 1:
			if obj[0].type == 'CAMERA':
				ctx.scene.camera = obj[0]
				bpy.ops.view3d.camera_to_view()
			else:
				bpy.ops.object.camera_add()
				ctx.scene.camera = bpy.data.objects[ctx.active_object.name]
				bpy.ops.view3d.camera_to_view()
		else:
			bpy.ops.object.camera_add()
			ctx.scene.camera = bpy.data.objects[ctx.active_object.name]
			bpy.ops.view3d.camera_to_view()
		
		self.report({'INFO'},'bpy.ops.camera.create_from_view()')
		return{"FINISHED"}

# Set as sctive camera
class Camera_OT_Set_Active(Operator):
	bl_idname = "camera.set_active"
	bl_label = "Set as Active Camera"
	bl_description = "Set Selected Camera As Active Camera"
	
	def execute(self, ctx):
		if ctx.active_object != None:
			if ctx.active_object.type == "CAMERA":
				ctx.scene.camera = ctx.active_object
				# if auto key is on bind marker to active camera
				if ctx.scene.tool_settings.use_keyframe_insert_auto:
					cur_frame = ctx.scene.frame_current
					name = "F_" + str(cur_frame)
					marker = ctx.scene.timeline_markers.new(name, frame = cur_frame)
					marker.camera = ctx.active_object
		self.report({'INFO'},'bpy.ops.camera.set_active()')
		return{"FINISHED"}

# Select Camera
class Camera_OT_Search(Operator):
	bl_idname = "camera.search"
	bl_label = "Serch Camera"
	bl_property = "SceneCameras"

	@classmethod
	def poll(self, ctx):
		return ctx.area.type == 'VIEW_3D'

	def scene_cameras(self, ctx):
		CamNameList = []
		for cam in bpy.data.objects:
			if cam.type == 'CAMERA':
				CamNameList.append((cam.name, cam.name, ''))
		return CamNameList

	SceneCameras: EnumProperty(items = scene_cameras)

	def execute(self, ctx):
		SelectedCamera = bpy.data.objects[self.SceneCameras]
		ctx.scene.camera = SelectedCamera
		area = next(area for area in ctx.screen.areas if area.type == 'VIEW_3D')
		area.spaces[0].region_3d.view_perspective = 'CAMERA'

		self.report({'INFO'},'bpy.ops.camera.search()')
		return {'FINISHED'}
	
	def invoke(self, ctx, event):
		wm = ctx.window_manager
		wm.invoke_search_popup(self)
		return {'FINISHED'}

class Camera_OT_Select(Operator):
	bl_idname = "camera.select"
	bl_label = "Select Camera"
	bl_description = "Select Active Camera"

	@classmethod
	def poll(self,ctx):
		return ctx.area.type == 'VIEW_3D'

	def set_cam(self,ctx,cameras):
		if len(cameras) == 1:
			ctx.scene.camera = cameras[0]
		elif len(cameras) > 1:
			bpy.ops.camera.search('INVOKE_DEFAULT')

	def execute(self,ctx):
		if ctx.active_object:
			if ctx.active_object.type == "CAMERA":
				if ctx.active_object.select_get():
					ctx.scene.camera = ctx.active_object
				else:
					cameras = [obj for obj in bpy.data.objects if obj.type == 'CAMERA']
					self.set_cam(ctx,cameras)
			else:
				cameras = [obj for obj in bpy.data.objects if obj.type == 'CAMERA']
				self.set_cam(ctx,cameras)
		else:
			if ctx.selected_objects:
				cameras = [obj for obj in ctx.selected_objects if obj.type == 'CAMERA']
				self.set_cam(ctx,cameras)
			else:
				cameras = [obj for obj in bpy.data.objects if obj.type == 'CAMERA']
				self.set_cam(ctx,cameras)
		
		if ctx.scene.camera:
			ctx.area.spaces[0].region_3d.view_perspective = 'CAMERA'
		
		self.report({'INFO'},'bpy.ops.camera.select()')
		return{"FINISHED"}

class Camera_OT_Lock_To_View_Toggle(Operator):
	bl_idname = "camera.lock_to_view_toggle"
	bl_label = "Lock Camera to view (Toggle)"
	bl_description = "Lock Active Camera to view"
	@classmethod

	def poll(self, ctx):
		return ctx.area.type == 'VIEW_3D'

	def execute(self, ctx):
		ctx.space_data.lock_camera = not ctx.space_data.lock_camera
		self.report({'INFO'},'bpy.ops.camera.lock_to_view_toggle()')
		return {'FINISHED'}

class Camera_OT_Lock_Transform(Operator):
	bl_idname = "camera.lock_transform"
	bl_label = "Lock Camera Transform"
	bl_description = "Lock active camera transform"

	@classmethod
	def poll(self, ctx):
		return ctx.area.type == 'VIEW_3D'

	def execute(self, ctx):
		cam = ctx.scene.camera
		if cam != None:
			state = not cam.lock_location[0]
			cam.lock_location = [state,state,state]
			cam.lock_rotation = [state,state,state]
			cam.lock_scale = [state,state,state]
		self.report({'INFO'},'bpy.ops.camera.lock_transform()')
		return {'FINISHED'}

class Camera_OT_Select_Active_Camera(Operator):
	bl_idname = "camera.select_active_camera"
	bl_label = "Select Active Camera/Target"
	bl_description = "Select Acitve Camera/Target"
	selcam: BoolProperty(name="Select Camera")
	seltrg: BoolProperty(name="Select Target")

	@classmethod
	def poll(self, ctx):
		return ctx.area.type == 'VIEW_3D'

	def execute(self, ctx):
		cam = ctx.scene.camera
		if cam != None:
			bpy.ops.object.select_all(action='DESELECT')
			if self.selcam:
				cam.select_set(state=True)
			if self.seltrg:
				if has_constraint(cam, 'TRACK_TO'):
					targ = cam.constraints["Track To"].target
					targ.select_set(state=True)
		self.report({'INFO'},'bpy.ops.camera.select_active_camera()')
		return {'FINISHED'}

class Camera_OT_Show_Safe_Area(Operator):
	bl_idname = "camera.show_safe_areas"
	bl_label = "Show Safe Area"
	bl_description = "Show Safe Area"

	@classmethod
	def poll(self, ctx):
		return ctx.area.type == 'VIEW_3D'

	def execute(self, ctx):
		cam = ctx.scene.camera
		if cam != None:
			cam.data.show_safe_areas = not cam.data.show_safe_areas
		
		self.report({'INFO'},'bpy.ops.camera.show_safe_areas()')
		return {'FINISHED'}

def camera_menu(self, ctx):
	layout = self.layout
	layout.separator()
	layout.operator("camera.create_from_view")
	layout.operator("camera.search")

classes = [Camera_OT_Set_Active,
			Camera_OT_Create_From_View,
			Camera_OT_Search,
			Camera_OT_Select,
			Camera_OT_Lock_To_View_Toggle,
			Camera_OT_Lock_Transform,
			Camera_OT_Select_Active_Camera,
			Camera_OT_Show_Safe_Area]

def register_cameras():
	[bpy.utils.register_class(c) for c in classes]
	bpy.types.VIEW3D_MT_view_cameras.append(camera_menu)

def unregister_cameras():
	bpy.types.VIEW3D_MT_view_cameras.remove(camera_menu)	
	[bpy.utils.unregister_class(c) for c in classes]