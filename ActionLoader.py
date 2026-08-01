bl_info = {
	"name": "Action Loader 中文版",
	"author": "Frederico Martins, vaner-org, spake404",
	"version": (5, 1, 1),
	"blender": (5, 1, 0),
	"location": "3D 视图 > 侧栏 > 动画",
	"description": "列出全部动作，并将选中的动作绑定到活动物体",
	"warning": "",
	"wiki_url": "https://github.com/spake404/ActionLoader",
	"tracker_url": "https://github.com/spake404/ActionLoader/issues",
	"category": "Animation",
	}

import bpy
import inspect
import sys
import os
global extra_info
extra_info = False

filter_name = ''
filter_name2 = ''
prev_mode = False
old_prevspeed = "0"


def action_fcurves(action, obj=None):
	"""Return F-Curves for a legacy action or the relevant Blender 5.1 slot."""
	if action is None:
		return ()

	legacy_fcurves = getattr(action, "fcurves", None)
	if legacy_fcurves is not None:
		return tuple(legacy_fcurves)

	slot_handle = None
	if obj and obj.animation_data and obj.animation_data.action == action:
		slot = obj.animation_data.action_slot
		if slot:
			slot_handle = slot.handle

	curves = []
	for layer in action.layers:
		for strip in layer.strips:
			if strip.type != 'KEYFRAME':
				continue
			for channelbag in strip.channelbags:
				if slot_handle is not None and channelbag.slot_handle != slot_handle:
					continue
				curves.extend(channelbag.fcurves)
	return tuple(curves)


def location_fcurves(action, obj=None):
	return tuple(
		curve for curve in action_fcurves(action, obj)
		if curve.data_path == "location" and curve.array_index in {0, 1, 2}
	)


def assign_action(obj, action):
	"""Assign an action while preserving the object's matching Action Slot."""
	if obj.animation_data is None:
		obj.animation_data_create()

	animation_data = obj.animation_data
	preferred_identifiers = []
	if animation_data.action_slot:
		preferred_identifiers.append(animation_data.action_slot.identifier)
	if animation_data.last_slot_identifier:
		preferred_identifiers.append(animation_data.last_slot_identifier)
	preferred_identifiers.append("OB" + obj.name)

	animation_data.action = action
	suitable_slots = tuple(animation_data.action_suitable_slots)
	for identifier in preferred_identifiers:
		matching_slot = next(
			(slot for slot in suitable_slots if slot.identifier == identifier),
			None,
		)
		if matching_slot:
			animation_data.action_slot = matching_slot
			break
	else:
		if animation_data.action_slot is None and len(suitable_slots) == 1:
			animation_data.action_slot = suitable_slots[0]

	return animation_data.action


def set_scene_range(scene, action, use_custom=False):
	if use_custom and "frame_start" in action and "frame_end" in action:
		start = int(action["frame_start"])
		end = int(action["frame_end"])
	else:
		start = int(action.frame_range[0])
		end = int(action.frame_range[1])

	scene.frame_preview_start = start
	scene.frame_preview_end = end
	scene.frame_start = start
	scene.frame_end = end
	return start, end


def set_prevspeed(self, value):
	global prev_mode 
	global old_prevspeed 
	old_prevspeed = bpy.context.scene.actionloader_speedprev
	if bpy.context.scene.actionloader_speedprev == "0":
		#print ("ZERO")
		prev_mode = bpy.context.scene.use_preview_range
	self["testprop"] = value
	
  
def get_prevspeed(self):
	#print("get")
	try:
		return self["testprop"];
	except:
		return 0;
	
def update_prevspeed(self, context):
	speed = bpy.context.scene.actionloader_speedprev
	ob = context.active_object
	scn = context.scene
	if ob is None or ob.animation_data is None or ob.animation_data.action is None:
		return
	ActiveAction = ob.animation_data.action

	if (
		scn.actionloader_rangemode == "0"
		and "frame_start" in ActiveAction
		and "frame_end" in ActiveAction
	):
		sframe = int(ActiveAction["frame_start"])
		eframe = int(ActiveAction["frame_end"])
	else:
		sframe = int(ActiveAction.frame_range[0])
		eframe = int(ActiveAction.frame_range[1])
	
	if speed == "0":
		scn.frame_start = sframe
		scn.frame_end = eframe
		scn.render.frame_map_new = 100
		if old_prevspeed == "1":
			scn.frame_current = int(scn.frame_current / 2 )
		elif old_prevspeed == "2":
			scn.frame_current =  int(scn.frame_current / 4 )
		elif old_prevspeed == "3":
			scn.frame_current =  int(scn.frame_current / 8)
		scn.use_preview_range = prev_mode
		
	elif speed == "1":
		scn.frame_start = sframe*2
		scn.frame_end = eframe*2
		scn.render.frame_map_new = 200
		if old_prevspeed == "0":
			scn.frame_current =  int(scn.frame_current * 2)
		elif old_prevspeed == "2":
			scn.frame_current =  int(scn.frame_current / 2 )
		elif old_prevspeed == "3":
			scn.frame_current =  int(scn.frame_current / 4 )
		scn.use_preview_range = False
	
	elif speed == "2":
		scn.frame_start = sframe*4
		scn.frame_end = eframe*4
		scn.render.frame_map_new = 400
		if old_prevspeed == "0":
			scn.frame_current =  int(scn.frame_current * 4)
		elif old_prevspeed == "1":
			scn.frame_current =  int(scn.frame_current * 2)
		elif old_prevspeed == "3":
			scn.frame_current =  int(scn.frame_current / 2)
		scn.use_preview_range = False
	
	elif speed == "3":
		scn.frame_start = sframe*8
		scn.frame_end = eframe*8
		scn.render.frame_map_new = 800
		if old_prevspeed == "0":
			scn.frame_current =  int(scn.frame_current * 8)
		elif old_prevspeed == "1":
			scn.frame_current =  int(scn.frame_current * 4)
		elif old_prevspeed == "2":
			scn.frame_current =  int(scn.frame_current * 2)
		scn.use_preview_range = False
	

def set_normal_speed():
	scn = bpy.context.scene
	if bpy.context.object == None or bpy.context.object.animation_data == None or bpy.context.object.animation_data.action == None:
		pass
	else:
		ActiveAction = bpy.context.active_object.animation_data.action
		if ActiveAction.get("frame_start") != None:
			scn.frame_start = int(ActiveAction["frame_start"])
			scn.frame_end = int(ActiveAction["frame_end"])
		else:
			scn.frame_start = int(ActiveAction.frame_range[0])
			scn.frame_end = int(ActiveAction.frame_range[1]) 

	scn.use_preview_range = prev_mode
	scn.actionloader_speedprev = '0'
	scn.render.frame_map_new = 100
 

def update_rangemode(self, context):
	ob = context.active_object
	if ob is None or ob.animation_data is None or ob.animation_data.action is None:
		return
	ActiveAction = ob.animation_data.action

	if context.scene.actionloader_rangemode == "0":
		if "frame_start" in ActiveAction and "frame_end" in ActiveAction:
			set_scene_range(context.scene, ActiveAction, use_custom=True)
	elif context.scene.actionloader_rangemode == "1":
		set_scene_range(context.scene, ActiveAction)
	
#def update_action_list_noObj(self, context):
#    pass

def save_action_extras():
	scn = bpy.context.scene
	ob = bpy.context.active_object
	if ob:
		if ob.animation_data is None or ob.animation_data.action is None:
			return
		ActiveAction = ob.animation_data.action
	else:
		if not bpy.data.actions or scn.action_list_index >= len(bpy.data.actions):
			return
		ActiveAction = bpy.data.actions[scn.action_list_index]
	
	ActiveAction.use_fake_user = True
	   
	## Assign start and end frame props to current action
	if scn.actionloader_rangemode == "0" and scn.actionloader_autorange:
		if scn.use_preview_range: 
			ActiveAction["frame_start"] = int(scn.frame_preview_start)
			ActiveAction["frame_end"] = int(scn.frame_preview_end)
		else:
			ActiveAction["frame_start"] = int(scn.frame_start)
			ActiveAction["frame_end"] = int(scn.frame_end   )
	

def update_action_list(self, context):
	#updates every time you pick action in the list
	ob = context.active_object
	#ob = context.object
	scn = context.scene
	if ob is None or not bpy.data.actions:
		return
	if ob.action_list_index < 0 or ob.action_list_index >= len(bpy.data.actions):
		return
	if scn.render.frame_map_new != 100:
		set_normal_speed()
	
	if ob.animation_data == None:
		action = 0 # No Animation data
	elif ob.animation_data.action == None:
		action = 1 # No Action
	else:
		action = 2 # Has Action
	
	if action == 2: # Has action
		save_action_extras()
	elif action == 0: # No Animation data
		ob.animation_data_create()

	# Then change the action and preserve the appropriate Blender 5.1 slot.
	ActiveAction = assign_action(ob, bpy.data.actions[ob.action_list_index])
	ActiveAction.use_fake_user = True

	# Changes the range on the scene
	if scn.actionloader_autorange:
		use_custom = (
			context.scene.actionloader_rangemode == "0"
			and "frame_start" in ActiveAction
			and "frame_end" in ActiveAction
		)
		set_scene_range(scn, ActiveAction, use_custom=use_custom)

	if scn.actionloader_1stFrame== True:
		scn.frame_current = scn.frame_start

	if scn.actionloader_autoplay and context.screen:
		if not context.screen.is_animation_playing:
			bpy.ops.screen.animation_play()

		"""
		#center stuff on dopesheet etc...
		for area in context.screen.areas:
			if area.type == 'DOPESHEET_EDITOR':
				for region in area.regions:
					if region.type == 'WINDOW':
						override = {'area': area, 'region': region, 'edit_object': context.edit_object}
						bpy.ops.action.view_all(override)
						
			elif area.type == 'GRAPH_EDITOR':
				for region in area.regions:
					if region.type == 'WINDOW':
						override = {'area': area, 'region': region, 'edit_object': context.edit_object}
						bpy.ops.graph.view_all(override)
			
			elif area.type == 'TIMELINE':
				for region in area.regions:
					if region.type == 'WINDOW':
						override = {'area': area, 'region': region, 'edit_object': context.edit_object}
						bpy.ops.time.view_all(override)    

		"""
		
class ACTION_UL_list2(bpy.types.UIList):
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
		self.use_filter_show = True
		ob = bpy.context.active_object
		#ob = bpy.context.object
		if self.layout_type in {'DEFAULT', 'COMPACT'}:
			if bpy.context.scene.actionloader_showicons:
				layout.prop(item, "name", text="", emboss=False, icon_value=icon)
			else: 
				layout.prop(item, "name", text="", emboss=False)
				#layout.operator("delete.action", text="", icon = "ERROR").delaction = bpy.data.actions[ob.action_list_index].name
				#layout.operator("ttt.action", text ="T").nome = str(self._DATA)
				#layout.label(text = "", icon = "ERROR")
		elif self.layout_type in {'GRID'}:
			pass
		global filter_name2
		filter_name2 = self.filter_name
		
class ACTION_UL_list(bpy.types.UIList):
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
		self.use_filter_show = True
		
		try:
			if "frame_end" in item and "frame_start" in item:
				durationf = item["frame_end"] - item["frame_start"]
			else:
				durationf = item.frame_range[1] - item.frame_range[0]
		except:
			durationf = 0
		durations = durationf / bpy.context.scene.render.fps if durationf > 0 else 0
			
		# Draw Info!  
		durations = durationf / bpy.context.scene.render.fps 
		info2 = str(durationf)+ " f. | "+ str(round(durations,6))+ " s. "
		
		
		if item.use_fake_user == True:
			fakeuser = "F"
		else:
			fakeuser = "X"
		
		info = str(item.users)+ fakeuser + " | " + str(len(item.pose_markers)) + "m | " + str(durationf) + "f | "+ str(round(durations,6))+ "s"
						
		if self.layout_type in {'DEFAULT', 'COMPACT'}:
			if bpy.context.scene.actionloader_showicons:
				layout.prop(item, "name", text="", emboss=False, icon_value=icon)
			else: 
				layout.prop(item, "name", text="", emboss=False)
			if extra_info:
				layout.label(text = info)
			
		elif self.layout_type in {'GRID'}:
			pass
		global filter_name
		filter_name = self.filter_name


class ActionLoaderPanel(bpy.types.Panel):
	"""在 3D 视图的动画侧栏中显示动作加载器"""
	bl_label = "动作加载器 5.1"
	bl_idname = "OBJECT_PT_action_loader"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "Animation"
	
	def draw(self, context):
		layout = self.layout
		scn = context.scene
		ob = context.active_object
		#ob = context.object
		
		animation = True
		if context.active_object != None:
			# Sets icon depending on what is selected and the current mode.
			if context.mode == "OBJECT":
				object_icon = "OUTLINER_OB_"+ str(ob.type)
				
			elif context.mode == "POSE":
				object_icon = "POSE_HLT"
			else:
				object_icon = str(ob.type) + "_DATA"
			
			row = layout.row(align = True)
			row.label (text = ob.name, icon = object_icon)
						
			if ob.animation_data and ob.animation_data.action:
				location_curves = location_fcurves(ob.animation_data.action, ob)
				if location_curves:
					mute_ico = "MUTE_IPO_ON" if all(
						curve.mute for curve in location_curves
					) else "MUTE_IPO_OFF"
					row.operator("muteloc.action", icon=mute_ico)
			
			row.operator ("object.deselect", icon = "X")
			info2 = "-f. | -s."
			
			if  ob.animation_data == None or ob.animation_data.action == None:
				info2 = "--f. | -s."
				if ob.animation_data == None:
					layout.label (text = "没有动画数据")
				elif ob.animation_data.action == None:
					layout.label (text = "没有绑定动作")

				layout.label(text = "提示：请先插入关键帧" , icon = "INFO")
			elif ob.animation_data.action:
				if ob.action_list_index > (len(bpy.data.actions)-1):
					action_icon = "ERROR" 
				elif bpy.data.actions[ob.action_list_index] != ob.animation_data.action:
					# When the active object's action is different than the one listed on the index
					action_icon = "ERROR"                     
				else: 
					action_icon = "ACTION"
				
				AA = ob.animation_data.action ##ActiveAction
				
				row = layout.row(align=True)
				row.label (text = AA.name, icon = action_icon)
					
				if action_icon == "ERROR":
					row.operator("fix.action", icon = "FILE_TICK")
				else:
					row.operator("duplicate.action", icon = "DUPLICATE")
					row.operator("unlinks.action", icon = "X")
								  
				if AA.use_fake_user:
					fakeuser= " [F]" 
				else:
					fakeuser= " [x]"
				try:
					if "frame_end" in AA and "frame_start" in AA:
						durationf = AA["frame_end"] - AA["frame_start"]
					else:
						durationf = AA.frame_range[1] - AA.frame_range[0]
				except:
					durationf = 0
				durations = durationf / bpy.context.scene.render.fps if durationf > 0 else 0
				
				info1 = AA.name 
				info2 = str(durationf)+ " f. | "+ str(round(durations,6))+ " s. "
				
				# Draw Info!            
				row = layout.row(align=True)
				row.label(text =  str(AA.users)+" 个使用者 "+fakeuser + " | " + str(len(AA.pose_markers))+" 个标记", icon = "INFO")
				row.operator("renderprev.action", icon = "RENDER_ANIMATION")
				
			if context.scene.actionloader_rangemode == '1':
				rangemode_icon = "KEYTYPE_MOVING_HOLD_VEC"
			else:
				rangemode_icon = "HANDLETYPE_FREE_VEC"
			  
			row = layout.row(align=True)
			row.label (text = info2, icon = "PREVIEW_RANGE")  
			row.label(icon = rangemode_icon)        
			list_context = ob
			"""
		elif context.active_object == None and len(bpy.data.actions) >=1:
			
			ListedAction = bpy.data.actions[bpy.context.scene.action_list_index]
			layout.label(text = "Tip: Select an Object", icon = "INFO")
			
			row = layout.row(align=True)
			row.label (text = ListedAction.name, icon = "ACTION")
			row.operator("duplicate.action", icon = "DUPLICATE")
						
			if ListedAction.use_fake_user:
					fakeuser= " [F]" 
			else:
					fakeuser= " [x]"
			if ListedAction.get("frame_end") == None:
				durationf = 0
				durations = 0
			else:
				durationf = ListedAction["frame_end"] - ListedAction["frame_start"]
			
			# Draw Info!  
			layout.label(text =  str(ListedAction.users)+"Users "+fakeuser + " | " + str(len(ListedAction.pose_markers))+"Markers", icon = "INFO")   
			
			durations = durationf / bpy.context.scene.render.fps 
			info2 = str(durationf)+ " f. | "+ str(round(durations,6))+ " s. "
			
			if context.scene.actionloader_rangemode == '1':
				rangemode_icon = "KEYTYPE_MOVING_HOLD_VEC"
			else:
				rangemode_icon = "HANDLETYPE_FREE_VEC"
			  
			row = layout.row(align=True)
			row.label (text = info2, icon = "PREVIEW_RANGE")  
			row.label(icon = rangemode_icon)              
			
			list_context = scn
			"""    
		else:
			layout.label (text= "Just start animating!", icon = "INFO")  
			list_context = scn
		
		#UIList - no object
		row = layout.row(align=True)
		row.template_list("ACTION_UL_list", "", bpy.data, "actions", list_context, "action_list_index")
		if bpy.context.scene.actionloader_DualView:
			row.template_list("ACTION_UL_list2", "", bpy.data, "actions", list_context, "action_list_index")
		
		## First View!!!!!!!!!!!!!!!!!!!1
		action_names= []
		for x in range (len(bpy.data.actions)):
			action_names.append(bpy.data.actions[x].name.lower())

		filtered_actions = [k for k in action_names if filter_name.lower() in k]
		
		total_anims=len(bpy.data.actions.items())
		listed_anims =len(filtered_actions)
		
		row = layout.row(align=True)
		
		if filter_name == "":
			row.label(text = "共 " + str(total_anims) +" 个动作", icon = "INFO")
		else:
			row.label(text = "显示 " + str(listed_anims)+ " / " +str(total_anims) +" 个动作", icon = "INFO")
		
		## DualView!!!!!!!!!!!!!!!!!!!!2
		if bpy.context.scene.actionloader_DualView:
			action_names= []
			for x in range (len(bpy.data.actions)):
				action_names.append(bpy.data.actions[x].name.lower())

			filtered_actions = [k for k in action_names if filter_name2.lower() in k]
			
			total_anims=len(bpy.data.actions.items())
			listed_anims =len(filtered_actions)
		
			if filter_name2 == "":
				row.label(text = "共 " + str(total_anims) +" 个动作", icon = "INFO")
			else:
				row.label(text = "显示 " + str(listed_anims)+ " / " +str(total_anims) +" 个动作", icon = "INFO")
		
		# DUAL VIEW ICON BT
		if scn.actionloader_DualView:
			dual_icon = "TRACKING_CLEAR_BACKWARDS"
		else:    
			dual_icon = "MOD_ARRAY"
		row.prop(scn, 'actionloader_DualView', text = "", icon = dual_icon)
		
		#Icons for Rangemode
		if context.scene.actionloader_rangemode == '1':
			rangemode_icon = "KEYTYPE_MOVING_HOLD_VEC"
		else:
			rangemode_icon = "HANDLETYPE_FREE_VEC"
		
		playback_row = layout.row(align=True)
		jump_start = playback_row.operator("screen.frame_jump", text="", icon="REW")
		jump_start.end = False
		is_playing = bool(context.screen and context.screen.is_animation_playing)
		playback_row.operator(
			"screen.animation_play",
			text="",
			icon="PAUSE" if is_playing else "PLAY",
		)
		jump_end = playback_row.operator("screen.frame_jump", text="", icon="FF")
		jump_end.end = True
		playback_row.prop(scn, "actionloader_autoplay", text="自动播放", toggle=True)

		layout.label(text = "预览速度：")
		
		layout.prop(context.scene, 'actionloader_speedprev', expand=True)
			 
		layout.label(text = "帧范围设置：")
		row = layout.row(align=True)
		row.prop(context.scene, 'actionloader_rangemode', expand=True )
		row.label(icon = rangemode_icon)
		layout.operator("setcustombyrange.action", icon = "FILE_REFRESH")
		
		#layout.operator("ttt.action", text ="TTTTTT###TTTTTTTT").nome = "conho"
		layout.label (text = "其他工具：")
		layout.operator("delete.action", icon = "ERROR")
		#.delaction = bpy.data.actions[ob.action_list_index].name

		layout.label(text= "选项：")

		layout.prop(scn, "actionloader_showicons", text="显示图标")
		layout.prop(scn, "actionloader_autorange", text="自动设置帧范围")
		layout.prop(scn, "actionloader_1stFrame", text="跳到第一帧")


class OBJECT_OT_SetActionRange(bpy.types.Operator):
	"""将当前时间轴范围保存到动作"""
	bl_idname = "set.actionrange"
	bl_label = "按时间轴设置动作范围"
	def execute(self, context):
		scn = context.scene
		ActiveAction = context.active_object.animation_data.action
		#print(ActiveAction)
		ActiveAction.use_fake_user = True
		
		if bpy.context.scene.use_preview_range:
			ActiveAction["frame_start"] = scn.frame_preview_start
			ActiveAction["frame_end"] = scn.frame_preview_end
		else:
			ActiveAction["frame_start"] = scn.frame_start
			ActiveAction["frame_end"] = scn.frame_end
		return{'FINISHED'} 


class OBJECT_OT_DeselectObject(bpy.types.Operator):
	"""取消活动物体，同时保留动作列表的编辑状态"""
	bl_idname = "object.deselect"
	bl_label = ""

	def execute(self, context):
		if context.scene.action_list_index < 0:
			context.scene.action_list_index = 0
   
		context.view_layer.objects.active = None
		
		#for obj in context.view_layer.selected_objects:
		#    print("OLA2") 
		#    obj.select_set(False)
		return {'FINISHED'}


class OBJECT_OT_DuplicateAction(bpy.types.Operator):
	"""复制当前动作"""
	bl_idname = "duplicate.action"
	bl_label = ""
	
	def execute(self, context):
		scn = bpy.context.scene
		ob = context.active_object
		save_action_extras()           
		if ob == None:
			newAnim = bpy.data.actions[scn.action_list_index].copy()
		else:
			newAnim = bpy.data.actions[bpy.context.object.action_list_index].copy()
			assign_action(ob, newAnim)
			quickfix_index()
		return{'FINISHED'}   


class OBJECT_OT_UnlinkAction(bpy.types.Operator):
	"""解除当前动作与活动物体的绑定"""
	bl_idname = "unlinks.action"
	bl_label = ""
	
	def execute(self, context):
		ob = context.active_object
		
		save_action_extras()
		ob.animation_data.action = None
		return{'FINISHED'}   


class OBJECT_OT_fixsync(bpy.types.Operator):
	"""修复动作列表与活动物体当前动作不一致的问题"""
	bl_idname = "fix.action"
	bl_label = "同步当前动作"
	
	def execute(self, context):
		quickfix_index()
		return{'FINISHED'}  


class OBJECT_OT_speedup(bpy.types.Operator):
	"""切换正常、1/2、1/4 和 1/8 预览速度（使用时间重映射）"""
	bl_idname = "speeddown.action"
	bl_label = ""
	
	def execute(self, context):
		ob = context.active_object
		#ob = context.object
		ActiveAction = ob.animation_data.action
		global prev_mode 
		
		if ob == None or ob.animation_data == None or ActiveAction == None:
			bpy.context.scene.render.frame_map_new = 100
		else:
			
			if (
				context.scene.actionloader_rangemode == "0"
				and "frame_start" in ActiveAction
				and "frame_end" in ActiveAction
			):
				sframe = int(ActiveAction["frame_start"])
				eframe = int(ActiveAction["frame_end"])
			else:
				sframe = int(ActiveAction.frame_range[0])
				eframe = int(ActiveAction.frame_range[1])
			
			if context.scene.render.frame_map_new == 100:
				context.scene.frame_start = int(sframe*2)
				context.scene.frame_end = int(eframe*2)
				context.scene.render.frame_map_new = 200
				context.scene.frame_current = context.scene.frame_current*2
				
				prev_mode = bpy.context.scene.use_preview_range 
				context.scene.use_preview_range = False
			elif context.scene.render.frame_map_new == 200:
				context.scene.frame_start = int(sframe*4)
				context.scene.frame_end = int(eframe*4)
				context.scene.render.frame_map_new = 400
				context.scene.frame_current = context.scene.frame_current*2
				context.scene.use_preview_range = False
			elif context.scene.render.frame_map_new == 400:
				context.scene.frame_start = int(sframe*8)
				context.scene.frame_end = int(eframe*8)
				context.scene.render.frame_map_new = 800
				context.scene.frame_current = context.scene.frame_current*2
				context.scene.use_preview_range = False
			else:
				bpy.context.scene.use_preview_range = prev_mode
				set_normal_speed()
		return{'FINISHED'} 


class OBJECT_OT_customByRange(bpy.types.Operator):
	"""根据动作首尾关键帧设置自定义帧范围"""
	bl_idname = "setcustombyrange.action"
	bl_label = "按关键帧重设范围"
	
	def execute(self, context):
		ob = context.active_object
		if not ob or not ob.animation_data or not ob.animation_data.action:
			return {'CANCELLED'}

		ActiveAction = ob.animation_data.action
		ActiveAction["frame_start"] = int(ActiveAction.frame_range[0])
		ActiveAction["frame_end"] = int(ActiveAction.frame_range[1])
		update_rangemode(self, bpy.context)
		return{'FINISHED'} 


class OBJECT_OT_renderprev(bpy.types.Operator):
	"""用动作名称渲染预览（输出路径应以“/”结尾且不含文件名）"""
	bl_idname = "renderprev.action"
	bl_label = ""

	directory: bpy.props.StringProperty(name="导出目录", subtype="DIR_PATH")
	filepath: bpy.props.StringProperty(name="导出路径", subtype="FILE_PATH")
	filename: bpy.props.StringProperty()

	def execute(self, context):
		scn = context.scene
		original_fp = scn.render.filepath
		original_fformat = scn.render.image_settings.file_format
		scn.render.filepath = os.path.splitext(os.path.join(self.directory, self.filepath))[0]

		scn.render.image_settings.file_format = "FFMPEG"
		scn.render.ffmpeg.format = "MPEG4"
		scn.render.ffmpeg.codec = "H264"

		bpy.ops.render.opengl(animation=True)

		scn.render.filepath = original_fp
		scn.render.image_settings.file_format = original_fformat

		return{'FINISHED'}

	def invoke(self, context, event):
		self.filename = context.object.animation_data.action.name + '.mp4'
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}


class OBJECT_OT_muter(bpy.types.Operator):
	"""启用或禁用物体位移曲线"""
	bl_idname = "muteloc.action"
	bl_label = ""
	def execute(self, context):
		ob = context.active_object
		if not ob or not ob.animation_data or not ob.animation_data.action:
			return {'CANCELLED'}

		curves = location_fcurves(ob.animation_data.action, ob)
		if not curves:
			self.report({'WARNING'}, "当前动作槽中没有物体位移曲线")
			return {'CANCELLED'}

		mute_to = not all(curve.mute for curve in curves)
		for curve in curves:
			curve.mute = mute_to
			curve.hide = mute_to
			curve.lock = mute_to
		return{'FINISHED'}

	
class OBJECT_OT_DeleteAction(bpy.types.Operator):
	"""警告：从 Blender 文件中永久删除所选动作"""
	bl_idname = "delete.action"
	bl_label = "删除所选动作"
	#delaction = bpy.props.StringProperty()
	def execute(self, context):
		#set_normal_speed()
		if not bpy.data.actions:
			return {'FINISHED'}

		ob = context.active_object
		if ob == None:
			ActionNR = context.scene.action_list_index
		else:
			ActionNR = context.object.action_list_index
		AA = bpy.data.actions[ActionNR] 
		
		if ob:
			ob.action_list_index = bpy.context.object.action_list_index-1
		else:
			bpy.context.scene.action_list_index = bpy.context.scene.action_list_index-1    
		
		bpy.data.actions.remove(AA, do_unlink=True)
		return{'FINISHED'} 
  
	
def quickfix_index():
	ob = bpy.context.object
	if ob is None or ob.animation_data is None or ob.animation_data.action is None:
		return
	for x in range(len(bpy.data.actions)):
		if bpy.data.actions[x] == ob.animation_data.action:
			ob.action_list_index = x
			break


def register():
	bpy.types.Scene.actionloader_DualView = bpy.props.BoolProperty(default= False, description = "显示两个动作列表，两个列表可以分别筛选；只改变显示方式，不修改场景")
	
	bpy.types.Object.action_list_index = bpy.props.IntProperty(
		override={"LIBRARY_OVERRIDABLE"}, 
		update = update_action_list, 
		description = "此物体在动作加载器列表中高亮显示的动作"
		)
	bpy.types.Scene.action_list_index = bpy.props.IntProperty(
		#update = update_action_list_noObj, 
		description = "没有选中物体时，场景动作列表中高亮显示的动作"
		)
	enum_items = (
		('0','自定义','使用当前帧范围作为动作范围'),
		('1','关键帧','使用动作的首尾关键帧设置范围')
		)
	bpy.types.Scene.actionloader_rangemode = bpy.props.EnumProperty(
		items = enum_items,
		update = update_rangemode,
		description = "选择使用自定义范围或动作的首尾关键帧"
		)
	enum_prevspeed = (
		('0','正常','使用正常速度预览，并将时间重映射设为 100'),
		('1','1/2', '使用一半速度预览，并将时间重映射设为 200'),
		('2','1/4', '使用四分之一速度预览，并将时间重映射设为 400'),
		('3','1/8', '使用八分之一速度预览，并将时间重映射设为 800')
		)
	bpy.types.Scene.actionloader_speedprev = bpy.props.EnumProperty(
		items = enum_prevspeed,
		update=update_prevspeed, 
		set = set_prevspeed, 
		get = get_prevspeed
		)
	bpy.types.Scene.actionloader_showicons = bpy.props.BoolProperty(
		name = "显示图标",
		description = "在动作加载器列表中显示动作图标",
		default = True
		)
	bpy.types.Scene.actionloader_autorange = bpy.props.BoolProperty(
		name = "自动设置帧范围",
		description = "选择动作时自动载入该动作的帧范围",
		default = False
		)
	bpy.types.Scene.actionloader_1stFrame = bpy.props.BoolProperty(
		name = "跳到动作第一帧",
		description = "选择动作后自动跳到该动作的第一帧",
		default = False
		)
	bpy.types.Scene.actionloader_autoplay = bpy.props.BoolProperty(
		name="自动播放",
		description="选择动作后自动开始播放时间轴",
		default=False,
		)

	for cls in module_classes:
		bpy.utils.register_class(cls[1])


def unregister():
	for cls in reversed(module_classes):
		bpy.utils.unregister_class(cls[1])

	del bpy.types.Object.action_list_index
	del bpy.types.Scene.action_list_index
	del bpy.types.Scene.actionloader_showicons
	del bpy.types.Scene.actionloader_autorange
	del bpy.types.Scene.actionloader_speedprev
	del bpy.types.Scene.actionloader_1stFrame
	del bpy.types.Scene.actionloader_autoplay
	del bpy.types.Scene.actionloader_rangemode
	del bpy.types.Scene.actionloader_DualView


module_classes = inspect.getmembers(sys.modules[__name__], inspect.isclass)


if __name__ == "__main__":
	register()
	
