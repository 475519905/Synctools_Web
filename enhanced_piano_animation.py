bl_info = {
    "name": "Enhanced MIDI PianoMotion Tools",
    "author": "475519905",
    "version": (2, 0),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > Piano",
    "description": "Enhanced MIDI piano animation with advanced features",
    "warning": "",
    "doc_url": "",
    "category": "Animation",
}

import bpy
import sys
import os
import json
from typing import Dict, List, Tuple, Optional

# 获取插件目录并添加 libs 路径
addon_dir = os.path.dirname(__file__)
lib_dir = os.path.join(addon_dir, "libs")
if lib_dir not in sys.path:
    sys.path.append(lib_dir)

try:
    import mido
except ImportError:
    raise ImportError("Mido library not found. Please ensure mido is installed in the plugin's libs directory.")

from bpy.types import Panel, Operator, PropertyGroup
from bpy.props import (
    StringProperty, PointerProperty, FloatProperty, 
    IntProperty, BoolProperty, EnumProperty, CollectionProperty
)
from bpy_extras.io_utils import ImportHelper

# 扩展设置属性组
class PianoKeySettings(PropertyGroup):
    # Key settings
    white_key_prefix: StringProperty(
        name="White Key Prefix",
        description="Prefix for white key object names",
        default="meshId57_name"
    )
    black_key_prefix: StringProperty(
        name="Black Key Prefix", 
        description="Prefix for black key object names",
        default="meshId56_name"
    )
    key_separator: StringProperty(
        name="Separator",
        description="Separator in object names",
        default="."
    )
    
    # Hammer settings
    hammer_prefix: StringProperty(
        name="Hammer Prefix",
        description="Prefix for hammer object names",
        default="pCube"
    )
    hammer_movement: FloatProperty(
        name="Hammer Movement",
        description="Distance the hammer moves upward",
        default=0.15,
        min=0.0,
        max=1.0
    )
    
    # Pedal settings
    damper_pedal: StringProperty(
        name="Damper Pedal",
        description="Object name for the damper pedal (right)",
        default="piano_pedal_metal01"
    )
    sostenuto_pedal: StringProperty(
        name="Sostenuto Pedal",
        description="Object name for the sostenuto pedal (middle)",
        default="piano_pedal_metal02"
    )
    una_corda_pedal: StringProperty(
        name="Una Corda Pedal",
        description="Object name for the una corda pedal (left)",
        default="piano_pedal_metal03"
    )
    pedal_rotation: FloatProperty(
        name="Pedal Rotation",
        description="Rotation angle when pedal is pressed (degrees)",
        default=7.0,
        min=0.0,
        max=45.0
    )
    
    # Animation settings
    key_rotation_angle: FloatProperty(
        name="Key Rotation Angle",
        description="Maximum rotation angle for keys (degrees)",
        default=7.0,
        min=0.0,
        max=15.0
    )
    animation_smoothing: FloatProperty(
        name="Animation Smoothing",
        description="Smoothing factor for animations (0=linear, 1=smooth)",
        default=0.5,
        min=0.0,
        max=1.0
    )
    velocity_sensitivity: FloatProperty(
        name="Velocity Sensitivity",
        description="How much velocity affects animation intensity",
        default=1.0,
        min=0.1,
        max=2.0
    )
    
    # Performance settings
    optimize_animations: BoolProperty(
        name="Optimize Animations",
        description="Remove redundant keyframes for better performance",
        default=True
    )
    max_keyframes_per_second: IntProperty(
        name="Max Keyframes/Second",
        description="Maximum keyframes per second to prevent overload",
        default=30,
        min=1,
        max=120
    )

class PianoAnimationPreset(PropertyGroup):
    name: StringProperty(name="Preset Name", default="")
    settings: StringProperty(name="Settings JSON", default="")

class PianoAnimationPresets(PropertyGroup):
    presets: CollectionProperty(type=PianoAnimationPreset)
    active_preset: IntProperty(name="Active Preset", default=0)

# 增强的测试操作符
class TestPianoComponents(Operator):
    bl_idname = "piano.test_components"
    bl_label = "Test Piano Components"
    bl_description = "Test if all piano component mappings are correct"

    def execute(self, context):
        settings = context.scene.piano_settings
        missing_components = []
        found_components = []
        
        # 测试白键
        white_keys_found = 0
        for i in range(1, 53):
            key_name = f"{settings.white_key_prefix}{settings.key_separator}{i}"
            if bpy.data.objects.get(key_name):
                white_keys_found += 1
            elif len(missing_components) < 5:  # 只报告前5个缺失的组件
                missing_components.append(f"White key {key_name}")

        # 测试黑键
        black_keys_found = 0
        for i in range(1, 37):
            key_name = f"{settings.black_key_prefix}{settings.key_separator}{i}"
            if bpy.data.objects.get(key_name):
                black_keys_found += 1
            elif len(missing_components) < 5:
                missing_components.append(f"Black key {key_name}")

        # 测试击锤
        hammers_found = 0
        for i in range(1, 89):
            hammer_name = f"{settings.hammer_prefix}{i}"
            if bpy.data.objects.get(hammer_name):
                hammers_found += 1
            elif len(missing_components) < 5:
                missing_components.append(f"Hammer {hammer_name}")

        # 测试踏板
        pedals = {
            "Damper Pedal": settings.damper_pedal,
            "Sostenuto Pedal": settings.sostenuto_pedal,
            "Una Corda Pedal": settings.una_corda_pedal
        }
        for pedal_type, pedal_name in pedals.items():
            if bpy.data.objects.get(pedal_name):
                found_components.append(f"{pedal_type}: {pedal_name}")
            else:
                missing_components.append(f"{pedal_type}: {pedal_name}")

        # 生成详细报告
        report_lines = []
        report_lines.append(f"White Keys: {white_keys_found}/52 found")
        report_lines.append(f"Black Keys: {black_keys_found}/36 found")
        report_lines.append(f"Hammers: {hammers_found}/88 found")
        
        if found_components:
            report_lines.append("Found Pedals:")
            for component in found_components:
                report_lines.append(f"  ✓ {component}")

        if missing_components:
            report_lines.append("Missing Components:")
            for component in missing_components:
                report_lines.append(f"  ✗ {component}")
            
            self.report({'WARNING'}, f"Some components missing. Check console for details.")
            print("\n".join(report_lines))
            return {'CANCELLED'}
        
        self.report({'INFO'}, f"All components found! White: {white_keys_found}, Black: {black_keys_found}, Hammers: {hammers_found}")
        print("\n".join(report_lines))
        return {'FINISHED'}

# 预设管理操作符
class SavePianoPreset(Operator):
    bl_idname = "piano.save_preset"
    bl_label = "Save Preset"
    bl_description = "Save current settings as a preset"

    def execute(self, context):
        settings = context.scene.piano_settings
        presets = context.scene.piano_presets
        
        # 创建设置字典
        settings_dict = {
            'white_key_prefix': settings.white_key_prefix,
            'black_key_prefix': settings.black_key_prefix,
            'key_separator': settings.key_separator,
            'hammer_prefix': settings.hammer_prefix,
            'hammer_movement': settings.hammer_movement,
            'damper_pedal': settings.damper_pedal,
            'sostenuto_pedal': settings.sostenuto_pedal,
            'una_corda_pedal': settings.una_corda_pedal,
            'pedal_rotation': settings.pedal_rotation,
            'key_rotation_angle': settings.key_rotation_angle,
            'animation_smoothing': settings.animation_smoothing,
            'velocity_sensitivity': settings.velocity_sensitivity,
            'optimize_animations': settings.optimize_animations,
            'max_keyframes_per_second': settings.max_keyframes_per_second
        }
        
        # 添加到预设集合
        preset = presets.presets.add()
        preset.name = f"Preset {len(presets.presets) + 1}"
        preset.settings = json.dumps(settings_dict)
        
        self.report({'INFO'}, f"Preset '{preset.name}' saved!")
        return {'FINISHED'}

class LoadPianoPreset(Operator):
    bl_idname = "piano.load_preset"
    bl_label = "Load Preset"
    bl_description = "Load a saved preset"

    def execute(self, context):
        presets = context.scene.piano_presets
        settings = context.scene.piano_settings
        
        if presets.active_preset >= len(presets.presets):
            self.report({'ERROR'}, "No preset selected!")
            return {'CANCELLED'}
        
        preset = presets.presets[presets.active_preset]
        settings_dict = json.loads(preset.settings)
        
        # 应用设置
        for key, value in settings_dict.items():
            if hasattr(settings, key):
                setattr(settings, key, value)
        
        self.report({'INFO'}, f"Preset '{preset.name}' loaded!")
        return {'FINISHED'}

# 优化的MIDI处理函数
def merge_tracks_optimized(midi_file, max_keyframes_per_second=30):
    """优化的MIDI处理，限制关键帧数量"""
    ticks_per_beat = midi_file.ticks_per_beat
    current_tempo = 500000
    events = []
    channel_details = {}
    last_keyframe_time = {}
    
    for track in midi_file.tracks:
        absolute_time = 0
        for msg in track:
            absolute_time += msg.time
            if msg.type == 'set_tempo':
                events.append((absolute_time, 'tempo', msg.tempo))
            elif msg.type in ['note_on', 'note_off'] and msg.velocity > 0:
                # 限制关键帧频率
                time_seconds = mido.tick2second(absolute_time, ticks_per_beat, current_tempo)
                if time_seconds - last_keyframe_time.get(msg.note, -1) >= 1.0 / max_keyframes_per_second:
                    events.append((absolute_time, 'note', msg))
                    last_keyframe_time[msg.note] = time_seconds
                    
                    channel = msg.channel
                    if channel not in channel_details:
                        channel_details[channel] = {'notes': 0, 'pitches': [], 'instrument': msg.program if hasattr(msg, 'program') else 'Unknown'}
                    channel_details[channel]['notes'] += 1
                    channel_details[channel]['pitches'].append(msg.note)
            elif msg.type == 'control_change' and msg.control in [64, 66, 67]:
                events.append((absolute_time, 'pedal', msg))

    events.sort(key=lambda x: x[0])
    messages, real_time, last_time = [], 0, 0
    
    for time, event_type, value in events:
        if event_type == 'tempo':
            real_time += mido.tick2second(time - last_time, ticks_per_beat, current_tempo)
            last_time = time
            current_tempo = value
        elif event_type in ['note', 'pedal']:
            real_time += mido.tick2second(time - last_time, ticks_per_beat, current_tempo)
            last_time = time
            messages.append((real_time, value))

    for channel, details in channel_details.items():
        details['average_pitch'] = sum(details['pitches']) / len(details['pitches']) if details['pitches'] else 0
    
    return messages, real_time, len(events), mido.tempo2bpm(current_tempo), channel_details

class PianoAnimationOperator(Operator, ImportHelper):
    """Enhanced MIDI piano animation operator"""
    bl_idname = "piano.create_animation"
    bl_label = "Create Piano Animation"
    
    filename_ext = ".mid"
    filter_glob: StringProperty(default='*.mid', options={'HIDDEN'}, maxlen=255)

    def create_note_to_key_mapping(self):
        settings = bpy.context.scene.piano_settings
        white_prefix = settings.white_key_prefix
        black_prefix = settings.black_key_prefix
        separator = settings.key_separator

        # 白键和黑键的MIDI音符映射
        white_keys = [21, 23, 24, 26, 28, 29, 31, 33, 35, 36, 38, 40, 41, 43, 45, 47, 48, 50, 52, 53, 55, 57, 59, 60, 62, 64, 65, 67, 69, 71, 72, 74, 76, 77, 79, 81, 83, 84, 86, 88, 89, 91, 93, 95, 96, 98, 100, 101, 103, 105, 107, 108]
        black_keys = [22, 25, 27, 30, 32, 34, 37, 39, 42, 44, 46, 49, 51, 54, 56, 58, 61, 63, 66, 68, 70, 73, 75, 78, 80, 82, 85, 87, 90, 92, 94, 97, 99, 102, 104, 106]
        
        note_to_key = {}
        for i, note in enumerate(white_keys):
            note_to_key[note] = f"{white_prefix}{separator}{i + 1}"
        for i, note in enumerate(black_keys):
            note_to_key[note] = f"{black_prefix}{separator}{i + 1}"
        return note_to_key

    def execute(self, context):
        try:
            # 清除现有动画
            bpy.ops.object.select_all(action='DESELECT')
            
            midi_file = mido.MidiFile(self.filepath)
            settings = context.scene.piano_settings
            
            # 创建琴键动画
            note_to_key = self.create_note_to_key_mapping()
            messages, total_time, note_count, bpm, channel_details = merge_tracks_optimized(
                midi_file, settings.max_keyframes_per_second
            )
            
            # 创建所有动画
            self.animate_piano_keys(messages, note_to_key)
            self.animate_piano_hammers(messages, note_to_key)
            self.animate_piano_pedals(messages)
            self.animate_piano_dampers(messages)
            
            # 优化动画
            if settings.optimize_animations:
                self.optimize_animations()
            
            # 显示处理结果
            minutes, seconds = divmod(int(total_time), 60)
            self.report({'INFO'}, 
                f"Animation created! Duration: {minutes}m {seconds}s, "
                f"Notes: {note_count}, BPM: {bpm:.1f}"
            )
            
            return {'FINISHED'}
            
        except Exception as e:
            self.report({'ERROR'}, f"Error creating animation: {str(e)}")
            return {'CANCELLED'}

    def animate_piano_keys(self, messages, note_to_key):
        scene = bpy.context.scene
        settings = scene.piano_settings
        fps = scene.render.fps
        
        for time_seconds, msg in messages:
            if msg.type in ['note_on', 'note_off']:
                frame = int(time_seconds * fps)
                note = msg.note
                velocity = msg.velocity if msg.type == 'note_on' else 0
                key_name = note_to_key.get(note)
                
                if key_name:
                    key = bpy.data.objects.get(key_name)
                    if key:
                        # 清除现有动画
                        if key.animation_data and key.animation_data.action:
                            key.animation_data.action = None
                        
                        key.rotation_euler[0] = 0
                        key.keyframe_insert(data_path="rotation_euler", frame=frame - 1)
                        
                        if msg.type == 'note_on':
                            # 使用设置中的参数
                            rotation_angle = (velocity / 127) * settings.key_rotation_angle * settings.velocity_sensitivity
                            duration_frames = max(1, int(15 - (velocity / 8.5) * settings.velocity_sensitivity))
                            
                            key.rotation_euler[0] = rotation_angle * (3.14159 / 180)
                            key.keyframe_insert(data_path="rotation_euler", frame=frame)
                            key.rotation_euler[0] = 0
                            key.keyframe_insert(data_path="rotation_euler", frame=frame + duration_frames)

    def animate_piano_hammers(self, messages, note_to_key):
        settings = bpy.context.scene.piano_settings
        scene = bpy.context.scene
        fps = scene.render.fps
        
        for time_seconds, msg in messages:
            if msg.type in ['note_on', 'note_off']:
                frame = int(time_seconds * fps)
                note = msg.note
                key_number = note - 20
                hammer_name = f"{settings.hammer_prefix}{key_number}"
                hammer = bpy.data.objects.get(hammer_name)
                
                if hammer:
                    original_z = hammer.location.z
                    hammer.location.z = original_z
                    hammer.keyframe_insert(data_path="location", index=2, frame=frame - 1)
                    
                    if msg.type == 'note_on':
                        duration_frames = max(1, int(15 - (msg.velocity / 8.5) * settings.velocity_sensitivity))
                        movement = settings.hammer_movement * (msg.velocity / 127) * settings.velocity_sensitivity
                        hammer.location.z = original_z + movement
                        hammer.keyframe_insert(data_path="location", index=2, frame=frame)
                        hammer.location.z = original_z
                        hammer.keyframe_insert(data_path="location", index=2, frame=frame + duration_frames)

    def animate_piano_pedals(self, messages):
        settings = bpy.context.scene.piano_settings
        scene = bpy.context.scene
        fps = scene.render.fps
        
        pedal_map = {
            64: settings.damper_pedal,
            66: settings.sostenuto_pedal,
            67: settings.una_corda_pedal,
        }
        
        for time_seconds, msg in messages:
            if msg.type == 'control_change' and msg.control in pedal_map:
                frame = int(time_seconds * fps)
                pedal_name = pedal_map[msg.control]
                pedal = bpy.data.objects.get(pedal_name)
                
                if pedal:
                    pedal.rotation_euler[0] = 0
                    pedal.keyframe_insert(data_path="rotation_euler", frame=frame - 1)
                    
                    if msg.value >= 64:
                        rotation_angle = settings.pedal_rotation * (3.14159 / 180)
                        pedal.rotation_euler[0] = rotation_angle
                        pedal.keyframe_insert(data_path="rotation_euler", frame=frame)
                    else:
                        pedal.rotation_euler[0] = 0
                        pedal.keyframe_insert(data_path="rotation_euler", frame=frame)
                        pedal.keyframe_insert(data_path="rotation_euler", frame=frame + 5)

    def animate_piano_dampers(self, messages):
        scene = bpy.context.scene
        fps = scene.render.fps
        pedal_map = {64: "PMain"}
        
        for time_seconds, msg in messages:
            if msg.type == 'control_change' and msg.control in pedal_map:
                frame = int(time_seconds * fps)
                pedal_name = pedal_map[msg.control]
                pedal = bpy.data.objects.get(pedal_name)
                
                if pedal:
                    pedal.location.z = 0
                    pedal.keyframe_insert(data_path="location", index=2, frame=frame - 1)
                    
                    if msg.value >= 64:
                        pedal.location.z = 0.02
                    else:
                        pedal.location.z = 0
                    
                    pedal.keyframe_insert(data_path="location", index=2, frame=frame)
                    
                    if msg.value < 64:
                        pedal.keyframe_insert(data_path="location", index=2, frame=frame + 5)

    def optimize_animations(self):
        """优化动画，移除冗余关键帧"""
        for obj in bpy.data.objects:
            if obj.animation_data and obj.animation_data.action:
                fcurves = obj.animation_data.action.fcurves
                for fcurve in fcurves:
                    # 简化曲线
                    fcurve.update()
                    if len(fcurve.keyframe_points) > 2:
                        # 移除过于接近的关键帧
                        points_to_remove = []
                        for i in range(1, len(fcurve.keyframe_points) - 1):
                            prev_point = fcurve.keyframe_points[i-1]
                            curr_point = fcurve.keyframe_points[i]
                            next_point = fcurve.keyframe_points[i+1]
                            
                            # 如果当前点与前后点值相同，标记为删除
                            if (abs(curr_point.co[1] - prev_point.co[1]) < 0.001 and 
                                abs(curr_point.co[1] - next_point.co[1]) < 0.001):
                                points_to_remove.append(i)
                        
                        # 从后往前删除，避免索引变化
                        for i in reversed(points_to_remove):
                            fcurve.keyframe_points.remove(fcurve.keyframe_points[i])

class PianoAnimationPanel(Panel):
    bl_label = "Enhanced Piano Animation"
    bl_idname = "VIEW3D_PT_piano_animation"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Piano'

    def draw(self, context):
        layout = self.layout
        settings = context.scene.piano_settings
        presets = context.scene.piano_presets
        
        # 预设管理
        preset_box = layout.box()
        preset_box.label(text="Presets", icon='PRESET')
        row = preset_box.row(align=True)
        row.prop(presets, "active_preset", text="")
        row.operator("piano.load_preset", text="Load", icon='IMPORT')
        row.operator("piano.save_preset", text="Save", icon='EXPORT')
        
        # Key settings
        key_box = layout.box()
        key_box.label(text="Key Settings", icon='OUTLINER_OB_FONT')
        col = key_box.column(align=True)
        col.prop(settings, "white_key_prefix")
        col.prop(settings, "black_key_prefix")
        col.prop(settings, "key_separator")
        col.prop(settings, "key_rotation_angle")
        
        # Hammer settings
        hammer_box = layout.box()
        hammer_box.label(text="Hammer Settings", icon='MODIFIER')
        col = hammer_box.column(align=True)
        col.prop(settings, "hammer_prefix")
        col.prop(settings, "hammer_movement")
        
        # Pedal settings
        pedal_box = layout.box()
        pedal_box.label(text="Pedal Settings", icon='MODIFIER_ON')
        col = pedal_box.column(align=True)
        col.prop(settings, "damper_pedal")
        col.prop(settings, "sostenuto_pedal")
        col.prop(settings, "una_corda_pedal")
        col.prop(settings, "pedal_rotation")
        
        # Animation settings
        anim_box = layout.box()
        anim_box.label(text="Animation Settings", icon='ANIM')
        col = anim_box.column(align=True)
        col.prop(settings, "velocity_sensitivity")
        col.prop(settings, "animation_smoothing")
        col.prop(settings, "optimize_animations")
        col.prop(settings, "max_keyframes_per_second")
        
        # 测试按钮
        layout.operator("piano.test_components", icon='CHECKMARK')
        
        # 动画创建按钮
        row = layout.row(align=True)
        row.scale_y = 2.0
        row.operator("piano.create_animation", icon='PLAY')

# 注册类列表
classes = (
    PianoKeySettings,
    PianoAnimationPreset,
    PianoAnimationPresets,
    TestPianoComponents,
    SavePianoPreset,
    LoadPianoPreset,
    PianoAnimationOperator,
    PianoAnimationPanel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.piano_settings = PointerProperty(type=PianoKeySettings)
    bpy.types.Scene.piano_presets = PointerProperty(type=PianoAnimationPresets)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.piano_settings
    del bpy.types.Scene.piano_presets

if __name__ == "__main__":
    register()