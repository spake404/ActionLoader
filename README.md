# Action Loader for Blender 5.1 | 动作加载器 Blender 5.1 中文版

[中文](#中文说明) | [English](#english)

这是 [Action Loader](https://github.com/vaner-org/ActionLoader) 的 Blender 5.1
兼容中文分支。插件可以在 3D 视图侧栏中列出当前 `.blend` 文件里的全部动作，
并将选中的动作直接绑定到活动物体或骨架，适合快速浏览、筛选和预览大量动画。

This is a Blender 5.1-compatible Simplified Chinese fork of
[Action Loader](https://github.com/vaner-org/ActionLoader). It lists all Actions
in the current `.blend` and assigns the selected Action to the active object or
armature for fast animation browsing and previewing.

## 中文说明

### 主要功能

- 在 3D 视图的“动画”侧栏中浏览当前文件的全部动作。
- 点击动作名称即可将其绑定到当前选中的物体或骨架。
- 支持名称搜索、动作复制、解除绑定和删除。
- 提供播放、暂停、跳到首帧和跳到末帧按钮。
- 可在选中动作后自动播放，并自动设置时间轴帧范围。
- 支持正常、1/2、1/4 和 1/8 速度预览。
- 支持 Blender 5.1 的分层动作和 Action Slot。
- 切换动作时会尽量保留匹配的 Action Slot，适用于同一动作同时包含骨架和武器槽位的情况。
- 插件面板、按钮、选项和悬停提示均已汉化；动作数据名称不会被修改。

### 安装

1. 打开 [`zh-CN`](https://github.com/spake404/ActionLoader/tree/zh-CN) 分支并下载 `ActionLoader.py`。
2. 在 Blender 5.1 中打开 `编辑 > 偏好设置 > 插件`。
3. 点击右上角菜单，选择“从磁盘安装”，然后选择 `ActionLoader.py`。
4. 搜索并启用 `Action Loader 中文版`。
5. 将鼠标放在 3D 视图中并按 `N`，然后打开右侧的“动画”标签。

### 使用

1. 在物体模式或姿态模式下选中需要播放动画的物体或骨架。
2. 在“动作加载器 5.1”列表中点击动作名称。
3. 插件会将动作绑定到活动物体，并根据选项更新帧范围或开始播放。
4. 使用列表下方的搜索框筛选名称，例如 `ryu_idle`。

动作属于 Blender 文件中的独立数据块，并不会永久属于某一根骨架。选择动作前应先选中
目标骨架；骨骼名称和结构不匹配的动作可能无法正确播放。

### 面板选项

- **自动播放**：选择动作后立即播放时间轴。
- **预览速度**：仅调整预览速度，可选择正常、1/2、1/4 或 1/8。
- **自定义 / 关键帧**：使用动作保存的自定义范围，或根据首尾关键帧计算范围。
- **自动设置帧范围**：切换动作时自动更新场景起止帧。
- **跳到第一帧**：切换动作后跳到动作起始帧。
- **显示图标**：显示或隐藏动作列表图标。
- **删除所选动作**：从当前 Blender 文件中解除引用并永久删除所选动作，使用前请备份。

### Blender 5.1 兼容改动

- 从活动 Action Slot 的 Channel Bag 中读取 F-Curve。
- 切换动作时匹配并保留适合当前物体的 Action Slot。
- 更新物体位移曲线的静音功能，使其支持 Blender 5.1 分层动作。
- 增加播放控制和自动播放。
- 对空物体、空动画数据、无动作和无效列表索引增加保护。
- 禁用插件时正确清理所有注册属性。

### 兼容性测试

使用 Blender 5.1 执行：

```powershell
blender.exe --factory-startup --background --python tests/blender_compat_test.py
```

测试会创建包含骨架和工具槽位的分层动作，检查动作切换、槽位保留、帧范围更新，
以及位移曲线静音是否只影响活动槽位。

## English

### Features

- Browse every Action in the current file from the 3D View's `Animation` sidebar.
- Assign an Action to the selected object or armature with one click.
- Search, duplicate, unlink, and delete Actions.
- Play, pause, and jump to the first or last frame.
- Optionally start playback and update the timeline range when an Action is selected.
- Preview at normal, 1/2, 1/4, or 1/8 speed.
- Support Blender 5.1 layered Actions and Action Slots.
- Preserve a matching Action Slot when switching Actions, including Actions with separate rig and weapon slots.
- Provide a Simplified Chinese interface without renaming animation data.

### Installation

1. Open the [`zh-CN`](https://github.com/spake404/ActionLoader/tree/zh-CN) branch and download `ActionLoader.py`.
2. In Blender 5.1, open `Edit > Preferences > Add-ons`.
3. Open the menu in the upper-right corner, choose `Install from Disk`, and select `ActionLoader.py`.
4. Search for and enable `Action Loader 中文版`.
5. Place the pointer over the 3D View, press `N`, and open the `Animation` tab.

### Usage

1. Select the target object or armature in Object Mode or Pose Mode.
2. Click an Action in the `动作加载器 5.1` list.
3. The add-on assigns that Action to the active object and optionally updates the frame range or starts playback.
4. Use the search field below the list to filter names such as `ryu_idle`.

Actions are independent Blender data-blocks and do not permanently belong to a
specific armature. Select the target armature before choosing an Action. An
Action may not play correctly when its bone names or rig structure do not match.

### Panel Options

- **自动播放 / Auto Play**: start timeline playback after selecting an Action.
- **预览速度 / Preview Speed**: preview at normal, 1/2, 1/4, or 1/8 speed.
- **自定义 / 关键帧**: use a stored custom range or derive the range from keyframes.
- **自动设置帧范围 / Set Auto Range**: update the scene range when switching Actions.
- **跳到第一帧 / Jump to First Frame**: move to the Action's first frame after switching.
- **显示图标 / Show Icons**: show or hide icons in the Action list.
- **删除所选动作 / Delete Selected Action**: unlink and permanently remove the selected Action from the current file. Back up first.

### Blender 5.1 Compatibility Changes

- Read F-Curves from the active Action Slot's Channel Bag.
- Match and preserve a suitable Action Slot when switching Actions.
- Update object-location muting for Blender 5.1 layered Actions.
- Add playback controls and optional Auto Play.
- Guard against missing objects, animation data, Actions, and invalid list indices.
- Clean up all registered properties when the add-on is disabled.

### Compatibility Test

Run with Blender 5.1:

```powershell
blender.exe --factory-startup --background --python tests/blender_compat_test.py
```

The test creates a layered Action with separate rig and tool slots, switches
Actions, verifies slot preservation and frame-range updates, and confirms that
location muting only affects the active slot.

## 来源与许可 | Credits and License

This fork is based on
[vaner-org/ActionLoader](https://github.com/vaner-org/ActionLoader), which is
based on the original
[frederico4d/ActionLoader](https://github.com/frederico4d/ActionLoader).

本项目沿用上游项目的 GPL-3.0 许可证。

GPL-3.0, inherited from the upstream project.
